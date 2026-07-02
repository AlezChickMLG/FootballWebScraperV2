import copy
import unittest

from src.football_repository.football_dataclasses import Match
from src.football_repository.football_dataclasses import SuturiObject
from src.football_repository.football_dataclasses.teams_dataclass import Team
from src.football_repository.repository import Repository


class TestsSuturi(unittest.TestCase):
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

        self.suturi = SuturiObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            xGOT=2.16,
            xG=2.1,
            total_suturi=20,
            suturi_pe_poarta=4,
            suturi_pe_langa_poarta=8,
            suturi_blocate=4,
            suturi_din_interiorul_careului=5,
            suturi_din_afara_careului=2,
            bare=1,
            goluri_marcate_cu_capul=1
        )

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_insert_teams_and_matches(self):
        self.repository.insert_team(self.team)
        self.repository.insert_team(self.another_team)
        self.repository.insert_match(self.match)

    def test_insert_suturi_correct(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.insert_suturi(self.suturi)
        self.assertTrue(
            result,
            "Nu am putut insera statistica"
        )

    def test_foreign_key_team(self):
        self.helper_insert_teams_and_matches()
        self.suturi.team_id = "alabala"

        result = self.repository.insert_suturi(self.suturi)
        self.assertFalse(
            result,
            "Am putut insera o echipa inexistenta"
        )

    def test_foreign_key_match(self):
        self.helper_insert_teams_and_matches()
        self.suturi.mid = "alabala"

        result = self.repository.insert_suturi(self.suturi)
        self.assertFalse(
            result,
            "Am putut insera un meci inexistent"
        )

    def test_unique_suturi(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_suturi(self.suturi)

        another_suturi = copy.copy(self.suturi)
        result = self.repository.insert_suturi(another_suturi)
        self.assertFalse(
            result,
            "Am putut insera o statistica pentru un meci existent pentru o echipa existenta"
        )

    def test_get_suturi(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_suturi(self.suturi)

        suturi = self.repository.get_suturi_by_id(self.suturi.mid, self.suturi.team_id)

        self.assertIsNotNone(suturi, "A fost returnat un None")
        self.assertIsInstance(suturi, SuturiObject, "A fost returnat un tip gresit de obiect")
        self.assertEqual(suturi, self.suturi, "A fost returnat obiectul gresit")

if __name__ == "__main__":
    unittest.main()