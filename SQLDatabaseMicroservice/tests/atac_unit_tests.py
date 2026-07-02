import copy
import unittest

from football_dataclasses.atac_dataclass import AtacObject
from football_dataclasses.matches_dataclass import Match
from football_dataclasses.teams_dataclass import Team
from repository import Repository


class TestsAtac(unittest.TestCase):
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

        self.atac = AtacObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            atingeri_in_careul_advers=10,
            pase_filtrante_reusite=5,
            ofsaiduri=2,
            lovituri_libere=4
        )

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_insert_teams_and_matches(self):
        self.repository.insert_team(self.team)
        self.repository.insert_team(self.another_team)
        self.repository.insert_match(self.match)

    def test_insert_atac_correct(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.insert_atac(self.atac)
        self.assertTrue(
            result,
            "Nu am putut insera statistica"
        )

    def test_foreign_key_team(self):
        self.helper_insert_teams_and_matches()
        self.atac.team_id = "alabala"

        result = self.repository.insert_atac(self.atac)
        self.assertFalse(
            result,
            "Am putut insera o echipa inexistenta"
        )

    def test_foreign_key_match(self):
        self.helper_insert_teams_and_matches()
        self.atac.mid = "alabala"

        result = self.repository.insert_atac(self.atac)
        self.assertFalse(
            result,
            "Am putut insera un meci inexistent"
        )

    def test_unique_atac(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_atac(self.atac)

        another_atac = copy.copy(self.atac)
        result = self.repository.insert_atac(another_atac)
        self.assertFalse(
            result,
            "Am putut insera o statistica pentru un meci existent pentru o echipa existenta"
        )

    def test_get_atac(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_atac(self.atac)

        atac = self.repository.get_atac_by_id(self.atac.mid, self.atac.team_id)

        self.assertIsNotNone(atac, "A fost returnat un None")
        self.assertIsInstance(atac, AtacObject, "A fost returnat un tip gresit de obiect")
        self.assertEqual(atac, self.atac, "A fost returnat obiectul gresit")

if __name__ == "__main__":
    unittest.main()