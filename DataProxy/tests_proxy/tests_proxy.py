import unittest
from unittest.mock import MagicMock

from football_repository.repository import Repository
from football_scraper.web_scraper import FlashscoreWebScraper

from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.matches_dataclass import Match

from src.football_proxy.proxy import Proxy

class ProxyTestCase(unittest.TestCase):
    def setUp(self):
        self.proxy = Proxy.__new__(Proxy)
        self.proxy.flashscoreWebScraper = MagicMock()
        self.proxy.repository = Repository(":memory:")

        self.team = Team(
            team_id="abcdef",
            team_name="Mexic",
            url="some_url"
        )

        self.another_team = Team(
            team_id="xyz",
            team_name="Canada",
            url="another_url"
        )

        self.match = Match(
            mid="123",
            home_team="abcdef",
            away_team="xyz",
            start_time="10.05.2026",
            match_url="facebuci.ro",
            match_score="0:3"
        )

        self.not_played_match = Match(
            mid="lmnop",
            home_team="abcdef",
            away_team="xyz",
            start_time="03.06.2026",
            match_url="facebuci.org",
            match_score="0:3",
            is_played=False
        )

        self.another_match = Match(
            mid="lmn",
            home_team="abcdef",
            away_team="xyz",
            start_time="05.07.2026",
            match_url="facebuci.com",
            match_score="0:3"
        )

    def test_get_team_database(self):
        self.proxy.repository.insert_team(self.team)
        team = self.proxy.get_team(self.team.team_name)

        self.assertIsNotNone(
            team,
            "Nu a returnat o echipa"
        )

        self.assertEqual(
            team,
            self.team,
            "Nu a returnat tipul corect de obiect"
        )

    def test_get_team_scraper(self):
        self.proxy.flashscoreWebScraper.get_team_url.return_value = self.team
        team = self.proxy.get_team(self.team.team_name)

        self.assertIsNotNone(
            team,
            "Nu a returnat o echipa"
        )

        self.assertEqual(
            team,
            self.team,
            "Nu a returnat tipul corect de obiect"
        )

        inserted_team = self.proxy.get_team(self.team.team_name)
        self.assertIsNotNone(
            team,
            "Nu a returnat o echipa"
        )

        self.assertEqual(
            team,
            self.team,
            "Nu a returnat tipul corect de obiect"
        )

    def test_get_matches_run_scraper(self):
        result = self.proxy.repository.insert_team(self.team)
        self.assertTrue(result)

        result = self.proxy.repository.insert_team(self.another_team)
        self.assertTrue(result)

        self.match.is_played = False
        result = self.proxy.repository.insert_match(self.match)
        self.assertTrue(result)

        self.another_match.is_played = False
        result = self.proxy.repository.insert_match(self.another_match)
        self.assertTrue(result)

        result = self.proxy.repository.insert_match(self.not_played_match)
        self.assertTrue(result)

        all_matches = self.proxy.get_matches(home_team=self.team.team_id)
        self.assertIsNotNone(
            all_matches,
            "Nu au fost returnate meciurile"
        )

        self.assertIsInstance(
            all_matches,
            list,
            "Nu a fost returnata colectia potrivita"
        )

        for match in all_matches:
            self.assertIsInstance(
                match,
                Match,
                "Nu a fost returnat obiectul potrivit"
            )

if __name__ == '__main__':
    unittest.main()
