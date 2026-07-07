import unittest

from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject

from src.football_scraper.data_processor import DataProcessor


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.data_processor = DataProcessor()

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

    def test_process_statistics(self):
        statistics = self.data_processor.process_statistics(mid=self.match.mid, home_team_id=self.match.home_team, away_team_id=self.match.away_team, statistics=self.stats)
        self.assertIsInstance(statistics, tuple, "Nu a fost returnata colectia potrivita")
        self.assertTrue(len(statistics) == 2, "Dimensiunea gresita")
        for team_stats in statistics:
            all_classes = [object.__class__ for object in team_stats.values()]
            self.assertIn(TopStatisticsObject, all_classes,
                          f"Nu a fost gasita un obiect de tip TopStatisticsObject in lista")
            self.assertIn(SuturiObject, all_classes,
                          f"Nu a fost gasita un obiect de tip SuturiObject in lista")
            self.assertIn(AtacObject, all_classes,
                          f"Nu a fost gasita un obiect de tip AtacObject in lista")
            self.assertIn(PaseObject, all_classes,
                          f"Nu a fost gasita un obiect de tip PaseObject in lista")
            self.assertIn(PortarObject, all_classes,
                          f"Nu a fost gasita un obiect de tip Portarbject in lista")
            self.assertIn(TopStatisticsObject, all_classes,
                          f"Nu a fost gasita un obiect de tip TopStatisticsObject in lista")


if __name__ == '__main__':
    unittest.main()
