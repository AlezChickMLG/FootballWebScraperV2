import logging

from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject
from football_repository.repository import Repository
from football_scraper.Checkers.search_bar_checker import SearchBarChecker
from football_scraper.data_processor import DataProcessor
from football_scraper.web_scraper import FlashscoreWebScraper

logger = logging.getLogger(__name__)

# Statistics dataclass type -> the repository insert method for its table.
_STAT_INSERTERS = {
    TopStatisticsObject: "insert_top_statistic",
    SuturiObject: "insert_suturi",
    PaseObject: "insert_pase",
    AtacObject: "insert_atac",
    AparareObject: "insert_aparare",
    PortarObject: "insert_portar",
}

class Proxy:
    def __init__(self, headless=True, database_name="football_database"):
        self.flashscore_web_scraper = FlashscoreWebScraper(headless)
        self.data_processor = DataProcessor()
        self.search_bar_checker = SearchBarChecker()
        self.repository = Repository(database_name)

        # Read-side lookups used to decide whether a match's statistics are
        # already stored. Order is irrelevant — we only check for presence.
        self._stat_getters = [
            self.repository.get_top_statistics_by_id,
            self.repository.get_pase_by_id,
            self.repository.get_atac_by_id,
            self.repository.get_suturi_by_id,
            self.repository.get_aparare_by_id,
            self.repository.get_portari_by_id,
        ]

        self._getter_key = {
            self.repository.get_top_statistics_by_id: "top_statistics",
            self.repository.get_pase_by_id: "pase",
            self.repository.get_atac_by_id: "atac",
            self.repository.get_suturi_by_id: "suturi",
            self.repository.get_aparare_by_id: "aparare",
            self.repository.get_portari_by_id: "portari",
        }

    # ------------------------------------------------------------------ #
    #  Teams and search objects                                          #
    # ------------------------------------------------------------------ #
    def get_team(self, team_name):
        """Return a Team by name, scraping and storing it if not cached.
        Returns None when the search yields no exact match, False on error or
        when the matched result isn't actually a team."""
        try:
            team = self.repository.get_team_by_name(team_name)
            if team:
                return team

            team_url = self.flashscore_web_scraper.get_team_url(team_name)
            if team_url is None or team_url is False:
                return team_url

            endpoint_url = team_url

            # If the search returned a redirect endpoint, follow it to the real URL.
            if self.search_bar_checker.is_endpoint_url(team_url):
                self.flashscore_web_scraper.navigate_to_team_page_by_id(
                    team_name=team_name,
                    team_id=self.data_processor.get_id_from_endpoint_url(team_url),
                )
                team_url = self.flashscore_web_scraper.get_page_url()

            if not team_url or not self.search_bar_checker.is_team(team_url):
                return False

            team = self.data_processor.format_team_object_from_url(
                team_name=team_name, team_url=endpoint_url
            )
            self.repository.insert_team(team)
            self.repository.commit()
            return team
        except Exception as e:
            logger.error("Failed to get team %r: %s", team_name, e)
            return False

    def get_team_by_id(self, team_id):
        return self.repository.get_team_by_id(team_id)

    def get_competition(self, competition_name):
        """Returns a Competition object from competition_name, or False if not
        found / not a competition."""
        try:
            # Lookup is by name here — the id isn't known until we scrape.
            competition = self.repository.get_competition_by_name(competition_name)
            if competition:
                return competition

            competition_url = self.flashscore_web_scraper.get_team_url(team_name=competition_name)
            if not competition_url:  # None or False
                return False

            if self.search_bar_checker.is_endpoint_url(competition_url):
                self.flashscore_web_scraper.navigate_to_team_page_by_id(
                    team_name=competition_name,
                    team_id=self.data_processor.get_id_from_endpoint_url(competition_url),
                )
                competition_url = self.flashscore_web_scraper.get_page_url()

            if not competition_url or not self.search_bar_checker.is_competition(competition_url):
                return False

            competition = self.data_processor.format_competition_object_from_full_url(competition_url)
            self.repository.insert_competition(competition)
            self.repository.commit()
            return competition
        except Exception as e:
            logger.error("Failed to get competition %r: %s", competition_name, e)
            return False


    # ------------------------------------------------------------------ #
    #  Matches                                                           #
    # ------------------------------------------------------------------ #
    def get_match_by_mid(self, mid):
        """Returns a single match object by mid"""
        return self.repository.get_match_by_id(mid=mid)

    def get_matches(self, team_name=None, team_id=None):
        """Return the stored matches for a team, scraping them on a cache miss.
        Both team_name and team_id are required."""
        if not (team_name and team_id):
            return None

        stored = self._get_stored_matches(team_id)
        if stored:
            return stored

        return self._scrape_and_store_matches(team_name, team_id)

    def scan_matches(self, team_name=None, team_id=None):
        """Scrape matches, even if they already exist in the database"""
        if not (team_name and team_id):
            return None

        return self._scrape_and_store_matches(team_name, team_id)

    def _get_stored_matches(self, team_id):
        """Matches where the team played either home or away, or None."""
        try:
            home = self.repository.get_match_by_details(home_team=team_id) or []
            away = self.repository.get_match_by_details(away_team=team_id) or []
            combined = [*home, *away]
            return combined if combined else None
        except Exception as e:
            logger.error("Failed to read stored matches for %s: %s", team_id, e)
            return None

    def _scrape_and_store_matches(self, team_name, team_id):
        """Scrape a team's matches, upsert the teams and matches, return them."""
        try:
            raw_matches = self.flashscore_web_scraper.get_all_matches(
                team_name=team_name, team_id=team_id
            )
            if not raw_matches:
                logger.warning("Scraper returned no matches for %s", team_name)
                return []

            formatted = self.data_processor.format_matches(raw_matches)
            if not formatted:
                logger.warning("No matches could be formatted for %s", team_name)
                return []

            stored_matches = []
            for entry in formatted:
                self._upsert_team(entry["home_team"])
                self._upsert_team(entry["away_team"])
                self.repository.insert_match(entry["match"])
                stored_matches.append(entry["match"])

            self.repository.commit()
            return stored_matches
        except Exception as e:
            logger.error("Failed to scrape matches for %s: %s", team_name, e)
            return False

    def _upsert_team(self, team):
        """Insert a team, falling back to update if it already exists."""
        if team.team_name:
            team.team_name = team.team_name.title().replace("-", " ")
        if not self.repository.insert_team(team):
            self.repository.update_team(team)

    # ------------------------------------------------------------------ #
    #  Statistics                                                        #
    # ------------------------------------------------------------------ #
    def get_statistics_for_matches(self, matches: list[Match]):
        """Return {mid: {team_id: stats}} for the given matches, scraping and
        storing any that aren't cached yet."""
        try:
            statistics = {}
            for match in matches:
                statistics[match.mid] = self._statistics_for_match(match)
            self.repository.commit()
            return statistics
        except Exception as e:
            logger.error("Failed to build statistics: %s", e)
            return None

    def get_match_statistics(self, match):
        """Return {'home_team_id': list(statistics), 'away_team_id': list(statistics)} for a single match"""
        try:
            statistics = self._statistics_for_match(match)
            self.repository.commit()
            return statistics
        except Exception as e:
            logger.error("Failed to build statistics for match %s: %s", match.mid, e)

    def _statistics_for_match(self, match):
        """Return {team_id: stats} for one match, scraping if not stored."""
        if self._match_statistics_stored(match):
            return {
                match.home_team: self._read_stored_statistics(match.mid, match.home_team),
                match.away_team: self._read_stored_statistics(match.mid, match.away_team),
            }
        return self._scrape_and_store_statistics(match)

    def _match_statistics_stored(self, match):
        """True if every statistics table already has a row for this match's
        home team (a match is scraped for both teams together, so home is enough)."""
        return all(
            getter(mid=match.mid, team_id=match.home_team) is not None
            for getter in self._stat_getters
        )

    def _read_stored_statistics(self, mid, team_id):
        """All stored statistics objects for one (match, team), by category."""
        return {
            self._getter_key[getter]: getter(mid=mid, team_id=team_id) for getter in self._stat_getters
        }

    def _scrape_and_store_statistics(self, match):
        """Scrape a match's statistics, update team flags, store both teams'
        rows, and return {home_team: stats, away_team: stats} or None on failure."""
        raw_statistics = self.flashscore_web_scraper.get_statistics(match_url=match.match_url)
        if not raw_statistics:
            logger.warning("No statistics scraped for match %s", match.mid)
            return None

        # Flags are nice-to-have: a failure here shouldn't sink the whole call.
        flags = self.flashscore_web_scraper.get_team_flags_from_statistics()
        if flags and flags is not False:
            home_flag, away_flag = flags
            self.repository.update_team(Team(team_id=match.home_team, image_url=home_flag))
            self.repository.update_team(Team(team_id=match.away_team, image_url=away_flag))
        else:
            logger.warning("Could not retrieve team flags for match %s", match.mid)

        processed = self.data_processor.process_statistics(
            mid=match.mid,
            home_team_id=match.home_team,
            away_team_id=match.away_team,
            statistics=raw_statistics,
        )
        # process_statistics returns False on failure, a (home, away) tuple otherwise.
        if not processed:
            logger.warning("Statistics processing failed for match %s", match.mid)
            return None

        home_stats, away_stats = processed

        self._store_statistics(home_stats)
        self._store_statistics(away_stats)
        self.repository.commit()

        return {match.home_team: home_stats, match.away_team: away_stats}

    def _store_statistics(self, statistics_by_category):
        """Insert each statistics object using the inserter for its type."""
        for statistic in statistics_by_category.values():
            inserter_name = _STAT_INSERTERS.get(type(statistic))
            if inserter_name is None:
                logger.error("No inserter for %s", type(statistic))
                continue
            getattr(self.repository, inserter_name)(statistic)


if __name__ == "__main__":
    proxy = Proxy()