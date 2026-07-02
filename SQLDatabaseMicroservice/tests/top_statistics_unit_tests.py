import copy
import unittest

from src.football_repository.football_dataclasses import Match
from src.football_repository.football_dataclasses.teams_dataclass import Team
from src.football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject
from src.football_repository.repository import Repository


class TestsTopStatistics(unittest.TestCase):
    def setUp(self):
        self.repository = Repository(":memory:")

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
            start_time="maine la pranz",
            match_url="facebuci.ro",
            match_score="0:3"
        )

        self.another_match = Match(
            mid="lmn",
            home_team="123",
            away_team="456",
            start_time="maine la pranz",
            match_url="facebuci.com",
            match_score="0:3"
        )

        self.top_statistics = TopStatisticsObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            xG=0.5,
            posesie_minge=75,
            total_suturi=20,
            suturi_pe_poarta=6,
            ocazii_mari=2,
            cornere=7,
            pase_procentaj=90,
            pase_reusite=400,
            pase_totale=450,
            cartonase_galbene=4,
            cartonase_rosii=1
        )

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_insert_teams_and_matches(self):
        self.repository.insert_team(self.team)
        self.repository.insert_team(self.another_team)
        self.repository.insert_match(self.match)

    def test_insert_top_statistics_correct(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.insert_top_statistic(self.top_statistics)
        self.assertTrue(
            result,
            "Nu am putut insera statistica"
        )

    def test_foreign_key_team(self):
        self.helper_insert_teams_and_matches()
        self.top_statistics.team_id = "alabala"

        result = self.repository.insert_top_statistic(self.top_statistics)
        self.assertFalse(
            result,
            "Am putut insera o echipa inexistenta"
        )

    def test_foreign_key_match(self):
        self.helper_insert_teams_and_matches()
        self.top_statistics.mid = "alabala"

        result = self.repository.insert_top_statistic(self.top_statistics)
        self.assertFalse(
            result,
            "Am putut insera un meci inexistent"
        )

    def test_unique_top_statistics(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_top_statistic(self.top_statistics)

        another_top_statistics = copy.copy(self.top_statistics)
        result = self.repository.insert_top_statistic(another_top_statistics)
        self.assertFalse(
            result,
            "Am putut insera o statistica pentru un meci existent pentru o echipa existenta"
        )

    def test_get_statistics(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_top_statistic(self.top_statistics)

        top_statistics = self.repository.get_top_statistics_by_id(self.top_statistics.mid, self.top_statistics.team_id)

        self.assertIsNotNone(top_statistics, "A fost returnat un None")
        self.assertIsInstance(top_statistics, TopStatisticsObject, "A fost returnat un tip gresit de obiect")
        self.assertEqual(top_statistics, self.top_statistics, "A fost returnat obiectul gresit")

if __name__ == "__main__":
    unittest.main()