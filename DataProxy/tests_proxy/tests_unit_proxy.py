import unittest
from re import match
from unittest.mock import MagicMock

from football_repository.repository import Repository
from football_scraper.data_processor import DataProcessor
from football_scraper.web_scraper import FlashscoreWebScraper

from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.matches_dataclass import Match

from src.football_proxy.proxy import Proxy

class ProxyTestCase(unittest.TestCase):
    def setUp(self):
        self.proxy = Proxy.__new__(Proxy)
        self.proxy.flashscore_web_scraper = MagicMock()
        self.proxy.repository = Repository(":memory:")
        self.proxy.data_processor = DataProcessor()

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

        self.some_team = Team(
            team_id="123",
            team_name="USA",
            url="other_url"
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
            away_team="123",
            start_time="05.07.2026",
            match_url="facebuci.com",
            match_score="0:3"
        )

        self.stats = {
            "Top statistici": {
                "Goluri așteptate (xG)": {"home": 0.13, "away": 1.46},
                "Posesie minge": {"home": "24%", "away": "76%"},
                "Total șuturi": {"home": 5, "away": 15},
                "Șuturi pe poartă": {"home": 0, "away": 5},
                "Ocazii mari": {"home": 0, "away": 2},
                "Cornere": {"home": 2, "away": 12},
                "Pase": {"home": "54%(98/183)", "away": "90%(510/569)"},
                "Cartonașe galbene": {"home": 0, "away": 3},
            },
            "Suturi": {
                "Goluri așteptate (xG)": {"home": 0.13, "away": 1.46},
                "xG pe poartă (xGOT)": {"home": 0.00, "away": 1.88},
                "Total șuturi": {"home": 5, "away": 15},
                "Șuturi pe poartă": {"home": 0, "away": 5},
                "Șuturi pe lângă poartă": {"home": 4, "away": 6},
                "Șuturi blocate": {"home": 1, "away": 4},
                "Șuturi din interiorul careului": {"home": 1, "away": 5},
                "Șuturi din afara careului": {"home": 4, "away": 10},
                "Bare": {"home": 0, "away": 0},
            },
            "Atac": {
                "Ocazii mari": {"home": 0, "away": 2},
                "Cornere": {"home": 2, "away": 12},
                "Atingeri în careul advers": {"home": 4, "away": 25},
                "Pase filtrante reușite": {"home": 0, "away": 0},
                "Ofsaiduri": {"home": 0, "away": 0},
                "Lovituri libere": {"home": 11, "away": 13},
            },
            "Pase": {
                "Pase": {"home": "54%(98/183)", "away": "90%(510/569)"},
                "Pase lungi": {"home": "22%(12/55)", "away": "62%(26/42)"},
                "Pase în treimea finală": {"home": "25%(13/51)", "away": "85%(199/233)"},
                "Centrări": {"home": "0%(0/5)", "away": "5%(1/22)"},
                "Pase de gol așteptate (xA)": {"home": 0.05, "away": 0.53},
                "Aruncări de la margine": {"home": 19, "away": 17},
            },
            "Aparare": {
                "Faulturi": {"home": 13, "away": 11},
                "Deposedări": {"home": "72%(21/29)", "away": "54%(7/13)"},
                "Dueluri câștigate": {"home": 49, "away": 56},
                "Respingeri": {"home": 22, "away": 27},
                "Intercepții": {"home": 14, "away": 10},
                "Erori care au dus la șut": {"home": 1, "away": 1},
                "Erori care au dus la gol": {"home": 0, "away": 0},
            },
            "Portari": {
                "Intervenții portar": {"home": 4, "away": 0},
                "xGOT împotrivă": {"home": 1.88, "away": 0.00},
                "Goluri prevenite": {"home": 0.88, "away": 0.00},
                "Aut de poartă": {"home": 12, "away": 7},
            },
        }

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
        self.proxy.flashscore_web_scraper.get_team_url.return_value = self.team
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
        self.not_played_match.is_played = False
        self.another_match.is_played = False
        self.helper_insert_teams_and_matches()

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

    def helper_insert_teams_and_matches(self):
        result = self.proxy.repository.insert_team(self.team)
        self.assertTrue(result, True)

        result = self.proxy.repository.insert_team(self.another_team)
        self.assertTrue(result, True)

        result = self.proxy.repository.insert_team(self.some_team)
        self.assertTrue(result, True)

        result = self.proxy.repository.insert_match(self.match)
        self.assertTrue(result, True)

        result = self.proxy.repository.insert_match(self.another_match)
        self.assertTrue(result, True)

        result = self.proxy.repository.insert_match(self.not_played_match)
        self.assertTrue(result, True)

    def test_scan_matches(self):
        self.proxy.flashscore_web_scraper.get_statistics.return_value = self.stats
        self.helper_insert_teams_and_matches()

        statistics = self.proxy.scan_matches_for_statistics([self.match, self.another_match])
        self.assertIsInstance(statistics, dict, "Colectie gresita")
        self.assertTrue(len(statistics.keys()) == 2, "Numar diferit de meciuri")

        self.assertIn(self.match.mid, statistics.keys(), f"Meci inexistent: {self.match.mid}")
        self.assertIn(self.another_match.mid, statistics.keys(), f"Meci inexistent: {self.another_match.mid}")

        for match, teams in statistics.items():
            self.assertTrue(len(teams.values()) == 2, "Numar diferit de echipe")

            repo_match = self.proxy.repository.get_match_by_id(match)
            self.assertIsNotNone(repo_match, f"Meci gol")

            self.assertIn(repo_match.home_team, teams.keys(), f"Nu exista echipa {repo_match.home_team}")
            self.assertIn(repo_match.away_team, teams.keys(), f"Nu exista echipa {repo_match.away_team}")

if __name__ == '__main__':
    unittest.main()
