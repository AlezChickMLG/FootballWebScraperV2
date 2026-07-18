import sys, os
import unittest
from datetime import datetime

from football_scraper.NameNormalizer.NameNormalizer import NameNormalizer
# adaugi radacina proiectului la path

from football_scraper.web_scraper import FlashscoreWebScraper

class TestIntegrationWebScraper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scraper = FlashscoreWebScraper(headless=False)
        cls.name_normalizer = NameNormalizer()

    @classmethod
    def tearDownClass(cls):
        cls.scraper.browser.close()
        cls.scraper.sync_playwright.stop()

    def setUp(self):
        self.scraper.reset_page()
        self.test_team = "Spania"

    def test_get_team_url_correct(self):
        expected_url = "bLyo6mco"

        url = self.scraper.get_team_url(self.test_team)
        self.assertIsNotNone(url)
        self.assertIn(expected_url, url)

    def test_get_team_url_no_search_results(self):
        url = self.scraper.get_team_url("Cimpanzeii")
        self.assertFalse(url)

    def test_get_team_url_wrong_spelling(self):
        url = self.scraper.get_team_url("Span")
        self.assertIsNone(url)

    def test_get_multiple_team_urls(self):
        #Spania
        expected_url = "bLyo6mco"

        url = self.scraper.get_team_url(self.test_team)
        self.assertIsNotNone(url)
        self.assertIn(expected_url, url)

        #Germania
        expected_url = "ptQide1O"
        self.test_team = "Germania"

        url = self.scraper.get_team_url(self.test_team)
        self.assertIsNotNone(url)
        self.assertIn(expected_url, url)

        #Argentina
        expected_url = "f9OppQjp"
        self.test_team = "Argentina"

        url = self.scraper.get_team_url(self.test_team)
        self.assertIsNotNone(url)
        self.assertIn(expected_url, url)

    def test_navigate_to_team_page(self):
        expected_url = "https://www.flashscore.ro/echipa/spania/bLyo6mco/"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        self.assertEqual(expected_url, self.scraper.page.url)

    def test_navigate_to_competition_page(self):
        expected_url = "https://www.flashscore.ro/fotbal/romania/superliga"
        test_competition = "Superliga"

        team_url = self.scraper.get_team_url(test_competition)
        self.scraper.navigate_to_team_page(team_url)

        self.assertTrue(self.scraper.get_page_url().startswith(expected_url), self.scraper.page.url)

    def test_navigate_to_team_page_by_id(self):
        expected_url = "https://www.flashscore.ro/echipa/capul-verde/MocyWdm7/"

        team_url = self.scraper.get_team_url("Capul Verde")
        self.scraper.navigate_to_team_page_by_id(team_name="Capul Verde", team_id=team_url.split(":")[-1])

        self.assertEqual(expected_url, self.scraper.page.url)

    def test_navigate_to_team_results(self):
        expected_url = "https://www.flashscore.ro/echipa/spania/bLyo6mco/rezultate/"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            print("A aparut tabul de rezultate", flush=True)
        except Exception as e:
            print("A expirat timeout-ul", flush=True)

        self.scraper.navigate_to_results_page()

        self.assertEqual(expected_url, self.scraper.page.url)

    def test_navigate_to_match(self):
        expected_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/?mid=8xM154oS"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            print("A aparut tabul de rezultate", flush=True)
        except Exception as e:
            print("A expirat timeout-ul", flush=True)

        self.scraper.navigate_to_results_page()
        self.scraper.navigate_to_match_page(expected_url)

        self.assertEqual(expected_url, self.scraper.page.url)

    def test_navigate_to_match_statistics(self):
        expected_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/sumar/statistici/total/?mid=8xM154oS"
        match_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/?mid=8xM154oS"

        team_url = self.scraper.get_team_url(self.test_team)
        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
            print("A aparut tabul de rezultate", flush=True)
        except Exception as e:
            print("A expirat timeout-ul", flush=True)

        self.scraper.navigate_to_results_page()
        self.scraper.navigate_to_match_page(match_url)
        self.scraper.navigate_to_statistics_tab()

        self.assertEqual(expected_url, self.scraper.page.url)

    '''Helper functions'''
    def helper_navigate_to_team_page_results(self):
        team_url = self.scraper.get_team_url(self.test_team)

        self.scraper.navigate_to_team_page(team_url)

        try:
            self.scraper.page.wait_for_selector("a.tabs__tab[title='Rezultate']")
        except Exception as e:
            print("A expirat timeout-ul")

        self.scraper.navigate_to_results_page()

    def helper_navigate_to_match_statistics(self):
        self.helper_navigate_to_team_page_results()

        match_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/?mid=8xM154oS"
        self.scraper.navigate_to_match_page(match_url)

        self.scraper.navigate_to_statistics_tab()

    def helper_navigate_to_competition_page(self, test_competition):
        competition_url = self.scraper.get_team_url(test_competition)
        self.scraper.navigate_to_competition_page(competition_url)
    '''Helper functions'''

    def test_scrape_competition_country(self):
        test_competition = "Superliga"

        self.helper_navigate_to_competition_page(test_competition)

        country_name = self.scraper._scrape_country_name()
        sanitized_country_name = self.name_normalizer.normalize_object_name(country_name)

        expected_country_name = "Romania"

        self.assertEqual(
            sanitized_country_name,
            expected_country_name,
            "Error: Different country names"
        )

    def test_scrape_competition_image_url(self):
        test_competition = "Superliga"

        self.helper_navigate_to_competition_page(test_competition)

        competition_image_url = self.scraper._scrape_competition_image_url()
        expected_starting_url = "https://static.flashscore.com/res/image/data"

        self.assertTrue(
            competition_image_url.startswith(expected_starting_url),
            "Error: Different starting substring"
        )

        self.assertTrue(
            competition_image_url.endswith("png"),
            "Error: Different extension"
        )

    def test_scrape_competition_dictionary(self):
        test_competition = "Superliga"
        competition_dict = self.scraper.scrape_competition_by_name(test_competition)

        sanitized_country_name = self.name_normalizer.normalize_object_name(competition_dict['country'])
        expected_country_name = "Romania"

        self.assertEqual(
            sanitized_country_name,
            expected_country_name,
            "Error: Different country names"
        )

        expected_starting_url = "https://static.flashscore.com/res/image/data"

        self.assertTrue(
            competition_dict['competition_image_url'].startswith(expected_starting_url),
            "Error: Different starting substring"
        )

        self.assertTrue(
            competition_dict['competition_image_url'].endswith("png"),
            "Error: Different extension"
        )

    def helper_test_get_all_matches(self, time_limit=None):
        team_url = self.scraper.get_team_url(self.test_team)

        all_matches = self.scraper.get_all_matches(team_url=team_url, time_limit=time_limit)
        self.assertIsNotNone(all_matches)
        self.assertGreater(len(all_matches), 0)

        for match in all_matches:
            self.assertIsInstance(match, dict)
            self.assertIn("home_team", match)
            self.assertIn("away_team", match)
            self.assertIn("match_url", match)
            self.assertIn("start_time", match)

            if time_limit:
                self.assertGreater(datetime.strptime(match['start_time'], "%d.%m.%Y"), time_limit, "A fost returnat un meci care se joaca dupa time_limit")

    def test_get_all_matches_correct(self):
        self.helper_test_get_all_matches()

    def test_get_all_matches_multiple_teams(self):
        self.helper_test_get_all_matches()

        self.test_team = "Germania"
        self.helper_test_get_all_matches()

        self.test_team = "Argentina"
        self.helper_test_get_all_matches()

    def test_get_all_matches_time_limit(self):
        time_limit = datetime(year=2026, month=2, day=10)
        self.helper_test_get_all_matches(time_limit)

    def test_get_all_statistics_correct(self):
        self.helper_navigate_to_match_statistics()
        statistics = self.scraper.get_statistics()

        self.assertIsNotNone(statistics)
        self.assertIsInstance(statistics, dict)
        self.assertGreater(len(statistics), 0)

    def test_get_flags_from_statistics_page(self):
        self.helper_navigate_to_match_statistics()

        home_team_image_url, away_team_image_url = self.scraper.get_team_flags_from_statistics()
        self.assertIsNotNone(home_team_image_url, "home url gol")
        self.assertIsNotNone(away_team_image_url, "away url gol")

        self.assertTrue(home_team_image_url != False, "Eroare la home url")
        self.assertTrue(away_team_image_url != False, "Eroare la away url")

        self.assertTrue(home_team_image_url.startswith('https://static.flashscore.com/res/image/data/'), "home link gresit")
        self.assertTrue(away_team_image_url.startswith('https://static.flashscore.com/res/image/data/'), "away link gresit")

        self.assertTrue(home_team_image_url.endswith('png'), "home format gresit")
        self.assertTrue(away_team_image_url.endswith('png'), "away format gresit")

    def test_get_flags_from_statistics_page_with_match_url(self):
        match_url = "https://www.flashscore.ro/meci/fotbal/spania-bLyo6mco/uruguay-xMk44orG/?mid=8xM154oS"

        home_team_image_url, away_team_image_url = self.scraper.get_team_flags_from_statistics(match_url=match_url)
        self.assertIsNotNone(home_team_image_url, "home url gol")
        self.assertIsNotNone(away_team_image_url, "away url gol")

        self.assertTrue(home_team_image_url != False, "Eroare la home url")
        self.assertTrue(away_team_image_url != False, "Eroare la away url")

        self.assertTrue(home_team_image_url.startswith('https://static.flashscore.com/res/image/data/'), "home link gresit")
        self.assertTrue(away_team_image_url.startswith('https://static.flashscore.com/res/image/data/'), "away link gresit")

        self.assertTrue(home_team_image_url.endswith('png'), "home format gresit")
        self.assertTrue(away_team_image_url.endswith('png'), "away format gresit")


if __name__ == "__main__":
    unittest.main()
