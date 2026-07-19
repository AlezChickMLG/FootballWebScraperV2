import unittest

from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.teams_dataclass import Team

from football_scraper.DataProcessor.data_processor import DataProcessor
from football_scraper.web_scraper import FlashscoreWebScraper


class DataProcessorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.flashscore_web_scraper = FlashscoreWebScraper(headless=False)
        self.data_processor = DataProcessor()

    def helper_format_team_by_url(self, team_name):
        team_url = self.flashscore_web_scraper.get_team_url(team_name)
        self.assertIsNotNone(team_url, "Echipa negasita")
        self.assertTrue(team_url != False, "Eroare in procesul de obtinere al echipei")

        team = self.data_processor.format_team_object_from_url(team_name=team_name, team_url=team_url)
        self.assertIsInstance(team, Team, "Obiect de tip gresit")

        self.flashscore_web_scraper.navigate_to_team_page_by_id(team_name=team_name, team_id=team.team_id)
        self.assertEqual(f"{team.url}/", self.flashscore_web_scraper.page.url, "Link gresit")

    def test_format_team_by_url_simple_name(self):
        self.helper_format_team_by_url("Spania")

    def test_format_team_by_url_complicated_name(self):
        self.helper_format_team_by_url("Capul Verde")

    def helper_format_team_by_id(self, team_name):
        team_id = self.flashscore_web_scraper.get_team_url(team_name).split(":")[-1]
        self.assertIsNotNone(team_id, "Echipa negasita")
        self.assertTrue(team_id != False, "Eroare in procesul de obtinere al echipei")

        team = self.data_processor.format_team_object_from_id(team_name=team_name, team_id=team_id)
        self.assertIsInstance(team, Team, "Obiect de tip gresit")

        self.flashscore_web_scraper.navigate_to_team_page_by_id(team_name=team_name, team_id=team.team_id)
        self.assertEqual(f"{team.url}/", self.flashscore_web_scraper.page.url, "Link gresit")

    def test_format_team_by_id_simple_name(self):
        self.helper_format_team_by_id("Spania")

    def test_format_team_by_id_complicated_name(self):
        self.helper_format_team_by_id("Capul Verde")

    def test_format_matches(self):
        team_name = "Spania"

        team_url = self.flashscore_web_scraper.get_team_url(team_name=team_name)
        self.assertIsNotNone(team_url, "URL gol")

        team_object = self.data_processor.format_team_object_from_url(team_name=team_name, team_url=team_url)
        self.assertIsNotNone(team_object, "Obiect gol")
        self.assertIsInstance(team_object, Team, "Obiect de tip gresit")
        self.assertIn(team_object.team_id, team_url, "Formatare invalida")

        matches = self.flashscore_web_scraper.get_all_matches(team_id=team_object.team_id, team_name=team_object.team_name)
        self.assertIsNotNone(matches, "Obiect gol")
        self.assertIsInstance(matches, list, "Colectia gresita")
        self.assertTrue(len(matches) != 0, "Lista goala")

        formatted_matches = self.data_processor.format_matches(matches)
        self.assertIsNotNone(formatted_matches, "Obiect gol")
        self.assertIsInstance(formatted_matches, list, "Colectia diferita")
        self.assertTrue(len(formatted_matches) != 0, "Colectie goala")

        for formatted_match in formatted_matches:
            self.assertIsInstance(formatted_matches['home_team'], Team, "Obiect gresit")
            self.assertIsInstance(formatted_matches['away_team'], Team, "Obiect gresit")
            self.assertIsInstance(formatted_matches['match'], Match, "Obiect gresit")


if __name__ == '__main__':
    unittest.main()
