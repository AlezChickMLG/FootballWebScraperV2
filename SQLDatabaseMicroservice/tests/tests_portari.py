import copy
import unittest

from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.repository import Repository


class TestsPortari(unittest.TestCase):
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

        self.portar = PortarObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            interventii_portar=5,
            xGOT_impotriva=1.64,
            goluri_prevenite=1.44,
            aut_de_poarta=12
        )

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_insert_teams_and_matches(self):
        self.repository.insert_team(self.team)
        self.repository.insert_team(self.another_team)
        self.repository.insert_match(self.match)

    def test_insert_portar_correct(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.insert_portar(self.portar)
        self.assertTrue(
            result,
            "Nu am putut insera statistica"
        )

    def test_foreign_key_team(self):
        self.helper_insert_teams_and_matches()
        self.portar.team_id = "alabala"

        result = self.repository.insert_portar(self.portar)
        self.assertFalse(
            result,
            "Am putut insera o echipa inexistenta"
        )

    def test_foreign_key_match(self):
        self.helper_insert_teams_and_matches()
        self.portar.mid = "alabala"

        result = self.repository.insert_portar(self.portar)
        self.assertFalse(
            result,
            "Am putut insera un meci inexistent"
        )

    def test_unique_portar(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_portar(self.portar)

        another_portar = copy.copy(self.portar)
        result = self.repository.insert_portar(another_portar)
        self.assertFalse(
            result,
            "Am putut insera o statistica pentru un meci existent pentru o echipa existenta"
        )

    def test_get_portar(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_portar(self.portar)

        portar = self.repository.get_portari_by_id(self.portar.mid, self.portar.team_id)

        self.assertIsNotNone(portar, "A fost returnat un None")
        self.assertIsInstance(portar, PortarObject, "A fost returnat un tip gresit de obiect")
        self.assertEqual(portar, self.portar, "A fost returnat obiectul gresit")

    def test_update(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_portar(self.portar)

        new_portar = PortarObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            interventii_portar=4,
            xGOT_impotriva=3.45
        )

        result = self.repository.update_portar(new_portar)
        self.assertTrue(
            result,
            "Update eronat"
        )

        result = self.repository.get_portari_by_id(
            mid=new_portar.mid,
            team_id=new_portar.team_id
        )

        self.assertEqual(
            result.interventii_portar,
            new_portar.interventii_portar,
            "interventii portar diferite"
        )

        self.assertEqual(
            result.xGOT_impotriva,
            new_portar.xGOT_impotriva,
            "xGOT_impotriva diferit"
        )

if __name__ == "__main__":
    unittest.main()