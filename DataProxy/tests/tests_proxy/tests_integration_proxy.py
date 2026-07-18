import unittest

from football_repository.football_dataclasses.competition_dataclass import Competition
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.repository import Repository
from football_scraper.data_processor import DataProcessor

from src.football_proxy.proxy import Proxy


class IntegrationProxy(unittest.TestCase):
    def setUp(self):
        super().__init__()
        self.proxy = Proxy(headless=False, database_name=":memory:")

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

    def test_get_team_incorrect(self):
        test_team = "Cimpanzeii"
        team = self.proxy.get_team(test_team)

        self.assertTrue(team is None or team is False, "A returnat o echipa inexistenta")

    def test_get_team_scraper(self):
        test_team = "Germania"
        team = self.proxy.get_team(test_team)

        self.assertIsNotNone(team, "Echipa nula")
        self.assertIsInstance(team, Team, "Obiect de tip gresit")
        self.assertTrue(team.team_name == test_team, "Echipa returnata gresit")

        database_team = self.proxy.repository.get_team_by_name(test_team)

        self.assertIsNotNone(database_team, "Echipa goala returnata de baza de date")
        self.assertEqual(team, database_team, "Echipa din baza de date difera de cea reala")

    def test_get_team_database(self):
        result = self.proxy.repository.insert_team(self.team)
        self.assertTrue(result)

        proxy_team = self.proxy.get_team(self.team.team_name)
        self.assertIsNotNone(proxy_team, "Echipa goala")
        self.assertIsInstance(proxy_team, Team, "Obiect de tip gresit")
        self.assertEqual(self.team, proxy_team, "Echipa diferite")

    def test_get_competition(self):
        test_competition = "Superliga"
        competition = self.proxy.get_competition(test_competition)

        self.assertIsNotNone(
            competition,
            "Error: None competition"
        )

        self.assertNotEqual(
            competition,
            False,
            "Error: Encountered an error"
        )

        self.assertIsInstance(
            competition,
            Competition,
            "Error: Different object type"
        )

        self.assertEqual(
            competition.competition_name,
            test_competition,
            "Error: Different competition name"
        )

    def test_get_all_matches_scraper(self):
        try:
            team = self.proxy.get_team(team_name="Spania")
            self.assertIsNotNone(team)

            matches = self.proxy.get_matches(team_name="Spania", team_id=team.team_id)
            self.assertIsNotNone(matches)

            for match in matches:
                #self.assertIsNotNone(self.proxy.repository.get_team_by_name(match['home_team'].team_name), f"Echipa {match['home_team'].team_name} nu exista in baza de date")
                #self.assertIsNotNone(self.proxy.repository.get_team_by_name(match['away_team'].team_name), f"Echipa {match['away_team'].team_name} nu exista in baza de date")
                self.assertIsNotNone(self.proxy.repository.get_match_by_id(match.mid),
                                     f"Meciul {match.mid} nu exista in baza de date")
        except Exception as e:
            print(f"Eroare la test: {e}")

    def test_get_all_matches_database(self):
        try:
            team = self.proxy.get_team(team_name="Norvegia")
            self.assertIsNotNone(team)

            matches = self.proxy.get_matches(team_name="Norvegia", team_id=team.team_id)
            self.assertIsNotNone(matches)

            for match in matches:
                self.assertIsNotNone(self.proxy.repository.get_match_by_id(match.mid),
                                     f"Meciul {match.mid} nu exista in baza de date")

            database_matches = self.proxy.get_matches(team_name="Norvegia", team_id=team.team_id)
            self.assertEqual(len(matches), len(database_matches), "Lista de meciuri diferite")

        except Exception as e:
            print(f"Eroare la test: {e}")

    def test_get_statistics_scraper(self):
        try:
            team_name = "Norvegia"

            team = self.proxy.get_team(team_name=team_name)
            self.assertIsNotNone(team, "Echipa goala")

            matches = self.proxy.get_matches(team_id=team.team_id, team_name=team.team_name)
            self.assertIsNotNone(matches, "Meciuri goale")

            statistics = self.proxy.get_statistics_for_matches(matches=matches[:10])
            self.assertIsNotNone(statistics, "Statistici goale")
            self.assertIsInstance(statistics, list, "Colectie gresita")
            self.assertTrue(len(statistics) != 0, "Colectie goala")

        except Exception as e:
            print(f"Error: {e}")


    def test_get_one_match_statistics_scraper(self):
        try:
            team_name = "Norvegia"

            team = self.proxy.get_team(team_name=team_name)
            self.assertIsNotNone(team, "Echipa goala")

            matches = self.proxy.get_matches(team_id=team.team_id, team_name=team.team_name)
            self.assertIsNotNone(matches, "Meciuri goale")

            statistics = self.proxy.get_match_statistics(matches[0])
            self.assertIsNotNone(statistics, "Statistici goale")
            self.assertIsInstance(statistics, dict, "Colectie gresita")
            self.assertTrue(len(statistics.keys()) == 2, "Numar diferit de statistici per echipa")

        except Exception as e:
            print(f"Error: {e}")

    def test_scan_matches(self):
        try:
            team_name = "Norvegia"

            team = self.proxy.get_team(team_name=team_name)
            self.assertIsNotNone(team, "Echipa goala")

            matches = self.proxy.scan_matches(team_id=team.team_id, team_name=team.team_name)
            self.assertIsNotNone(matches, "Meciuri goale")

            statistics = self.proxy.get_match_statistics(matches[0])
            self.assertIsNotNone(statistics, "Statistici goale")
            self.assertIsInstance(statistics, dict, "Colectie gresita")
            self.assertTrue(len(statistics.keys()) == 2, "Numar diferit de statistici per echipa")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    unittest.main()
