import copy
import unittest

from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.repository import Repository


class TestsPase(unittest.TestCase):
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

        self.pase = PaseObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            pase_procentaj=90,
            pase_reusite=450,
            pase_totale=500,
            pase_lungi_procentaj=75,
            pase_lungi_reusite=3,
            pase_lungi_totale=4,
            pase_in_treimea_finala_procentaj=75,
            pase_in_treimea_finala_reusite=3,
            pase_in_treimea_finala_totale=4,
            centrari_procentaj=75,
            centrari_reusite=3,
            centrari_totale=4,
            xA=1.75,
            aruncari_de_la_margine=30
        )

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_insert_teams_and_matches(self):
        self.repository.insert_team(self.team)
        self.repository.insert_team(self.another_team)
        self.repository.insert_match(self.match)

    def test_insert_pase_correct(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.insert_pase(self.pase)
        self.assertTrue(
            result,
            "Nu am putut insera statistica"
        )

    def test_foreign_key_team(self):
        self.helper_insert_teams_and_matches()
        self.pase.team_id = "alabala"

        result = self.repository.insert_pase(self.pase)
        self.assertFalse(
            result,
            "Am putut insera o echipa inexistenta"
        )

    def test_foreign_key_match(self):
        self.helper_insert_teams_and_matches()
        self.pase.mid = "alabala"

        result = self.repository.insert_pase(self.pase)
        self.assertFalse(
            result,
            "Am putut insera un meci inexistent"
        )

    def test_unique_pase(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_pase(self.pase)

        another_pase = copy.copy(self.pase)
        result = self.repository.insert_pase(another_pase)
        self.assertFalse(
            result,
            "Am putut insera o statistica pentru un meci existent pentru o echipa existenta"
        )

    def test_get_pase(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_pase(self.pase)

        pase = self.repository.get_pase_by_id(self.pase.mid, self.pase.team_id)

        self.assertIsNotNone(pase, "A fost returnat un None")
        self.assertIsInstance(pase, PaseObject, "A fost returnat un tip gresit de obiect")
        self.assertEqual(pase, self.pase, "A fost returnat obiectul gresit")

    def test_delete_top_statistics(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.delete_pase_by_id(self.match.mid, self.match.home_team)
        self.assertTrue(
            result,
            "Nu a fost efectuata stergerea cu succes a unui rand din pase"
        )

        result = self.repository.get_pase_by_id(self.match.mid, self.match.home_team)
        self.assertIsNone(
            result,
            "A fost returnat un obiect de tip pase"
        )


if __name__ == "__main__":
    unittest.main()