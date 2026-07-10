import copy
import unittest

from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.repository import Repository


class TestsAparare(unittest.TestCase):
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

        self.aparare = AparareObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            faulturi=12,
            deposedari_procentaj=75,
            deposedari_reusite=12,
            deposedari_totale=15,
            dueluri_castigate=20,
            respingeri=15,
            interceptii=10,
            erori_sut=1,
            erori_gol=1
        )

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_insert_teams_and_matches(self):
        self.repository.insert_team(self.team)
        self.repository.insert_team(self.another_team)
        self.repository.insert_match(self.match)

    def test_insert_aparare_correct(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.insert_aparare(self.aparare)
        self.assertTrue(
            result,
            "Nu am putut insera statistica"
        )

    def test_foreign_key_team(self):
        self.helper_insert_teams_and_matches()
        self.aparare.team_id = "alabala"

        result = self.repository.insert_aparare(self.aparare)
        self.assertFalse(
            result,
            "Am putut insera o echipa inexistenta"
        )

    def test_foreign_key_match(self):
        self.helper_insert_teams_and_matches()
        self.aparare.mid = "alabala"

        result = self.repository.insert_aparare(self.aparare)
        self.assertFalse(
            result,
            "Am putut insera un meci inexistent"
        )

    def test_unique_aparare(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_aparare(self.aparare)

        another_aparare = copy.copy(self.aparare)
        result = self.repository.insert_aparare(another_aparare)
        self.assertFalse(
            result,
            "Am putut insera o statistica pentru un meci existent pentru o echipa existenta"
        )

    def test_get_aparare(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_aparare(self.aparare)

        aparare = self.repository.get_aparare_by_id(self.aparare.mid, self.aparare.team_id)

        self.assertIsNotNone(aparare, "A fost returnat un None")
        self.assertIsInstance(aparare, AparareObject, "A fost returnat un tip gresit de obiect")
        self.assertEqual(aparare, self.aparare, "A fost returnat obiectul gresit")

    def test_delete_top_statistics(self):
        self.helper_insert_teams_and_matches()

        result = self.repository.delete_aparare_by_id(self.match.mid, self.match.home_team)
        self.assertTrue(
            result,
            "Nu a fost efectuata stergerea cu succes a unui rand din aparare"
        )

        result = self.repository.get_aparare_by_id(self.match.mid, self.match.home_team)
        self.assertIsNone(
            result,
            "A fost returnat un obiect de tip aparare"
        )

    def test_update(self):
        self.helper_insert_teams_and_matches()
        self.repository.insert_aparare(self.aparare)

        new_aparare = AparareObject(
            mid=self.match.mid,
            team_id=self.match.home_team,
            deposedari_totale=34,
            deposedari_procentaj=98
        )

        result = self.repository.update_aparare(new_aparare)
        self.assertTrue(
            result,
            "Update eronat"
        )

        result = self.repository.get_aparare_by_id(
            mid=new_aparare.mid,
            team_id=new_aparare.team_id
        )

        self.assertEqual(
            result.deposedari_totale,
            new_aparare.deposedari_totale,
            "deposedari totale diferite"
        )

        self.assertEqual(
            result.deposedari_procentaj,
            new_aparare.deposedari_procentaj,
            "deposedari reusite diferite"
        )


if __name__ == "__main__":
    unittest.main()