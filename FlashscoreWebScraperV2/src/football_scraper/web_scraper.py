import logging
from time import sleep

from football_scraper.NameNormalizer.NameNormalizer import NameNormalizer
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError

from football_scraper.DataProcessor.data_processor import DataProcessor

logger = logging.getLogger(__name__)

_FLASHSCORE_URL = "https://www.flashscore.ro/"
_FLASHSCORE_URL_NO_SLASH = "https://www.flashscore.ro"

# Default wait for a selector to appear, in milliseconds.
_DEFAULT_TIMEOUT = 10000

# (used when a match older than time_limit is reached).
_STOP = object()

# All the Flashscore CSS selectors in one place. When the site changes its
# markup, this is the only block that needs editing.
class _Selectors:
    COOKIE_ACCEPT = "#onetrust-accept-btn-handler"
    SEARCH_WINDOW = "#search-window"
    SEARCH_INPUT = ".searchInput__input"
    SEARCH_RESULT = ".searchResult"
    SEARCH_RESULT_NAME = ".searchResult__participantName"
    RESULTS_TAB = "a.tabs__tab[title='Rezultate']"
    HOME_PARTICIPANT = ".event__homeParticipant span"
    AWAY_PARTICIPANT = ".event__awayParticipant span"
    SCORE_ITEM = "span[data-testid='wcl-tableScore']"
    START_TIME = "span[data-testid='wcl-stageTime']"
    MATCH_LINK = ".eventRowLink"
    PARTICIPANT_LOGO = "img[data-testid=wcl-participantLogo]"
    STATISTICS_FILTER = ".filterOver div a"
    STATISTICS_SECTION = ".sectionsWrapper .section"
    STATISTIC_ITEM = "div[data-testid='wcl-statistics']"
    SECTION_HEADER = ".sectionHeader"
    DETAIL_FLAGS = ".container__detailInner .duelParticipant__container .participant__image"

class _CompetitionSelectors:
    COUNTRY_NAME = ".breadcrumb__link"
    COMPETITION_IMAGE = ".heading__logo"

class _MatchesSelectors:
    MATCHES_PARENT = "div[data-analytics-context='tab-results']"
    ALL_ELEMENTS = f"{MATCHES_PARENT}>section>div>div"
    MATCH = ".event__match"
    COMPETITION = ".headerLeague__wrapper"
    COMPETITION_NAME = "a.headerLeague__title"

def reset_decorator(func):
    """Return to the homepage before running the wrapped scraping method."""
    def wrapper(self, *args, **kwargs):
        self.reset_page()
        return func(self, *args, **kwargs)
    return wrapper


class FlashscoreWebScraper:
    def __init__(self, headless=True):
        self.sync_playwright = sync_playwright().start()
        self.browser = self.sync_playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        self.flashscore_url = _FLASHSCORE_URL
        self.flashscore_url_no_slash = _FLASHSCORE_URL_NO_SLASH

        self.data_processor = DataProcessor()
        self.name_normalizer = NameNormalizer()

        self.page.goto(self.flashscore_url)
        self._accept_cookies()

    def close(self):
        self.browser.close()
        self.sync_playwright.stop()

    def reset_page(self):
        self.page.goto(self.flashscore_url)

    def _accept_cookies(self):
        self.page.wait_for_selector(_Selectors.COOKIE_ACCEPT)
        self.page.click(_Selectors.COOKIE_ACCEPT)

    # ------------------------------------------------------------------ #
    #  Team search                                                       #
    # ------------------------------------------------------------------ #
    @reset_decorator
    def get_team_url(self, team_name):
        """Return the href of the search result whose name matches team_name.
        None if no exact match, False on timeout or error."""
        try:
            self._open_search(team_name)

            self.page.wait_for_selector(_Selectors.SEARCH_RESULT, timeout=_DEFAULT_TIMEOUT)
            results = self.page.query_selector_all(_Selectors.SEARCH_RESULT)

            for result in results:
                name_element = result.query_selector(_Selectors.SEARCH_RESULT_NAME)
                if name_element is None:
                    continue
                name = self.name_normalizer.normalize_object_name(name_element.inner_text())
                if name.strip().lower() == team_name.strip().lower():
                    return result.get_attribute("href")

            return None
        except PlaywrightTimeoutError:
            logger.warning("No teams found for %r", team_name)
            return False
        except Exception as e:
            logger.error("Error searching for team %r: %s", team_name, e)
            return False

    def _open_search(self, team_name):
        self.page.click(_Selectors.SEARCH_WINDOW)
        self.page.wait_for_selector(_Selectors.SEARCH_INPUT)
        self.page.fill(_Selectors.SEARCH_INPUT, team_name)

    # ------------------------------------------------------------------ #
    #  Competition search from main tab                                  #
    # ------------------------------------------------------------------ #

    def _scrape_country_name(self):
        return self.page.query_selector_all(_CompetitionSelectors.COUNTRY_NAME)[1].inner_text()

    def _scrape_competition_image_url(self):
        return self.page.query_selector(_CompetitionSelectors.COMPETITION_IMAGE).get_attribute("src")

    def scrape_competition_by_name(self, competition_name):
        """:returns { country: ..., competition_image_url: ..., url: .... }"""
        try:
            competition_url = self.get_team_url(competition_name)
            if not competition_url:
                return False

            self.navigate_to_competition_page(competition_url)

            return self.scrape_competition_page()

        except Exception as e:
            logger.error("Error scraping competition info by name: %s", e)

    def scrape_competition_by_url(self, competition_url):
        try:
            self.navigate_to_competition_page(competition_url)

            return self.scrape_competition_page()

        except Exception as e:
            logger.error("Error scraping competition info by url: %s", e)

    def scrape_competition_page(self):
        competition_dict = {}

        country_name = self._scrape_country_name()
        if country_name:
            competition_dict['country'] = country_name

        competition_image_url = self._scrape_competition_image_url()
        if competition_image_url:
            competition_dict['competition_image_url'] = competition_image_url

        competition_dict['url'] = self.get_page_url()

        return competition_dict

    def __scrape_competition_element(self, element):
        try:
            competition_element = element.query_selector(_MatchesSelectors.COMPETITION_NAME)

            return {
                'competition_name': competition_element.get_attribute("title"),
                'competition_href': competition_element.get_attribute("href")
            }

        except Exception as e:
            logger.error("Cannot scraper competition element: %s", e)
            return None

    # ------------------------------------------------------------------ #
    #  Matches                                                           #
    # ------------------------------------------------------------------ #
    def __is_match(self, element):
        class_attr = element.get_attribute("class") or ""
        return _MatchesSelectors.MATCH[1:] in class_attr.split()

    def __is_competition(self, element):
        class_attr = element.get_attribute("class") or ""
        return _MatchesSelectors.COMPETITION[1:] in class_attr.split()

    @reset_decorator
    def get_all_matches(self, team_id=None, team_name=None, team_url=None, time_limit=None):
        """Return a list of raw match dicts for a team's results page.
        Accepts either (team_id + team_name) or a direct team_url."""
        try:
            self._open_results_page(team_id, team_name, team_url)

            #match_elements = self.page.query_selector_all(_Selectors.MATCH)
            #logger.info("Found %d matches", len(match_elements))

            all_elements = self.page.query_selector_all(_MatchesSelectors.ALL_ELEMENTS)
            logger.info("Found %d elements", len(all_elements))

            matches = []
            competitions = []

            last_competition_scraped = None

            for element in all_elements:
                if self.__is_match(element):
                    parsed = self._parse_match_element(element, time_limit)
                    element_list = matches

                    if last_competition_scraped:
                        parsed['competition_details'] = last_competition_scraped

                elif self.__is_competition(element):
                    parsed = self.__scrape_competition_element(element)
                    element_list = competitions

                    last_competition_scraped = parsed

                else:
                    parsed = None
                    element_list = None

                    logger.error("Unknown element in results tab")

                if parsed is _STOP:
                    break
                if parsed is not None:
                    element_list.append(parsed)

            return competitions, matches
        except Exception as e:
            logger.error("Error retrieving matches: %s", e)
            return None

    def _open_results_page(self, team_id, team_name, team_url):
        """Navigate to a team's results page via id+name or direct url."""
        if team_id and team_name:
            self.navigate_to_team_page_by_id(team_id=team_id, team_name=team_name)
        elif team_url:
            self.navigate_to_team_page(team_url)
        else:
            return

        try:
            self.page.wait_for_selector(_Selectors.RESULTS_TAB)
        except Exception:
            logger.warning("Results tab did not appear in time")

        self.navigate_to_results_page()

    def _parse_match_element(self, match_element, time_limit):
        """Turn one .event__match element into a raw dict. Returns None to skip,
        or the _STOP sentinel when time_limit is reached (stop iterating)."""
        match_link = match_element.query_selector(_Selectors.MATCH_LINK)
        if not match_link:
            return None

        match_dict = {"match_url": match_link.get_attribute("href")}

        start_time_element = match_element.query_selector(_Selectors.START_TIME)
        if start_time_element:
            raw_start = start_time_element.inner_text()
            formatted_start, string_start = self.data_processor.process_start_time(raw_start)
            match_dict["start_time"] = string_start

            if time_limit and formatted_start and formatted_start < time_limit:
                return _STOP

        home = match_element.query_selector(_Selectors.HOME_PARTICIPANT)
        if home:
            match_dict["home_team"] = home.inner_text()

        score_tags = match_element.query_selector_all(_Selectors.SCORE_ITEM)
        if score_tags:
            score = ":".join(score_tag.inner_text() for score_tag in score_tags)
            match_dict["score"] = score

        away = match_element.query_selector(_Selectors.AWAY_PARTICIPANT)
        if away:
            match_dict["away_team"] = away.inner_text()

        logos = match_element.query_selector_all(_Selectors.PARTICIPANT_LOGO)
        if len(logos) >= 2:
            match_dict["home_team_image_url"] = logos[0].get_attribute("src")
            match_dict["away_team_image_url"] = logos[1].get_attribute("src")

        return match_dict

    # ------------------------------------------------------------------ #
    #  Statistics                                                        #
    # ------------------------------------------------------------------ #
    @reset_decorator
    def get_statistics(self, match_url=None):
        """Return {category: {stat_name: {home, away}}} for a match's stats tab."""
        try:
            if match_url:
                self.navigate_to_match_page(match_url)
                self.navigate_to_statistics_tab()
                self.page.wait_for_selector(_Selectors.STATISTICS_SECTION.split()[-1])

            self.page.wait_for_selector(_Selectors.STATISTIC_ITEM)
            sections = self.page.query_selector_all(_Selectors.STATISTICS_SECTION)
            if not sections:
                return {}

            statistics = {}
            for section in sections:
                title, section_stats = self._parse_statistics_section(section)
                if title is None:
                    return None
                statistics[title] = section_stats

            return statistics
        except Exception as e:
            logger.error("Error processing statistics: %s", e)
            return None

    def _parse_statistics_section(self, section):
        """Return (title, {stat_name: {home, away}}) for one stats section."""
        header = section.query_selector(_Selectors.SECTION_HEADER)
        if header is None:
            logger.error("Statistics section header not found")
            return None, None

        title = header.inner_text()
        section_stats = {}

        for item in section.query_selector_all(_Selectors.STATISTIC_ITEM):
            parsed = self._parse_statistic_item(item)
            if parsed is not None:
                name, values = parsed
                section_stats[name] = values

        return title, section_stats

    def _parse_statistic_item(self, item):
        """Return (stat_name, {home, away}) for one statistic row, or None if the
        row's markup doesn't match what we expect."""
        try:
            wrapper = item.query_selector("div")
            if wrapper is None:
                return None

            details = wrapper.query_selector_all("div")
            if len(details) < 3:
                return None

            home_value = "".join(el.inner_text() for el in details[0].query_selector_all("span"))
            away_value = "".join(el.inner_text() for el in details[2].query_selector_all("span"))

            name_element = details[1].query_selector("span")
            if name_element is None:
                return None
            name = name_element.inner_text()

            return name, {"home": home_value, "away": away_value}
        except Exception as e:
            logger.warning("Failed to parse a statistic row: %s", e)
            return None

    def get_team_flags_from_statistics(self, match_url=None):
        """Return (home_flag_url, away_flag_url) from a match's detail header."""
        try:
            if match_url:
                self.navigate_to_match_page(match_url)
                self.navigate_to_statistics_tab()

            flags = self.page.query_selector_all(_Selectors.DETAIL_FLAGS)[:2]
            home_flag, away_flag = (el.get_attribute("src") for el in flags)
            return home_flag, away_flag
        except Exception as e:
            logger.error("Error retrieving team flags: %s", e)
            return False

    # ------------------------------------------------------------------ #
    #  Navigation helpers                                                #
    # ------------------------------------------------------------------ #
    def navigate_to_team_page(self, team_url):
        self.page.goto(f"{self.flashscore_url}{team_url}")

    def navigate_to_competition_page(self, competition_url):
        self.page.goto(f"{self.flashscore_url}{competition_url}")
        sleep(5)

    def navigate_to_team_page_by_id(self, team_name, team_id):
        slug = team_name.lower().replace(" ", "-")
        self.page.goto(f"{self.flashscore_url_no_slash}/echipa/{slug}/{team_id}")

    def navigate_to_results_page(self):
        results_tab = self.page.query_selector(_Selectors.RESULTS_TAB)
        if results_tab is None:
            logger.warning("Results tab not found; staying on current page")
            return
        results_href = results_tab.get_attribute("href")
        self.page.goto(f"{self.flashscore_url_no_slash}{results_href}")

    def navigate_to_match_page(self, match_url):
        self.page.goto(match_url)

    def navigate_to_statistics_tab(self):
        buttons = self.page.query_selector_all(_Selectors.STATISTICS_FILTER)
        if len(buttons) < 2:
            logger.warning("Statistics tab button not found (found %d)", len(buttons))
            return
        statistics_href = buttons[1].get_attribute("href")
        self.page.goto(f"{self.flashscore_url_no_slash}{statistics_href}")

    def get_page_url(self):
        return self.page.url

if __name__ == "__main__":
    web_scraper = FlashscoreWebScraper()