import unittest

from src.football_repository.football_dataclasses.matches_dataclass import Match
from src.football_repository.football_dataclasses.teams_dataclass import Team
from repository import Repository


class TestsMatches(unittest.TestCase):
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

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_insert_teams_and_match(self):
        self.repository.insert_team(self.team)
        self.repository.insert_team(self.another_team)
        return self.repository.insert_match(self.match)

    def test_insert_match_correct(self):
        self.helper_insert_teams_and_match()

        self.repository.cursor.execute("SELECT * FROM Matches")
        result = self.repository.cursor.fetchone()

        self.assertIsNotNone(
            result,
            "Nu a fost gasit meciul in tabela"
        )

    def test_matches_foreign_key_matches(self):
        self.helper_insert_teams_and_match()

        # testarea unui meci care contine o echipe inexistenta
        self.match.away_team = "xyzt"
        result = self.repository.insert_match(self.match)
        self.assertFalse(
            result,
            "Am putut insera o echipa inexistenta"
        )

    def test_matches_unique_mid(self):
        self.helper_insert_teams_and_match()

        # testarea unicitatii mid
        result = self.repository.insert_match(self.another_match)
        self.assertFalse(
            result,
            "Am putut insera doua meciuri cu acelasi mid"
        )

    def test_matches_same_teams_different_start_time(self):
        self.helper_insert_teams_and_match()

        # testarea meciurilor cu aceleasi echipe, dar timpi de start diferiti
        self.another_match.home_team = "abcdef"
        self.another_match.away_team = "xyz"
        self.another_match.start_time = "maine seara"

        result = self.repository.insert_match(self.another_match)
        self.assertTrue(
            result,
            f"Nu am putut insera doua meciuri cu aceleasi echipe, dar timpi de start diferiti"
        )

    def test_matches_unique_details(self):
        self.helper_insert_teams_and_match()

        self.another_match.home_team = "abcdef"
        self.another_match.away_team = "xyz"

        result = self.repository.insert_match(self.another_match)
        self.assertFalse(
            result,
            f"Am putut insera doua meciuri cu aceleasi echipe si cu acelasi timp de start"
        )

    def test_matches_unique_url(self):
        self.helper_insert_teams_and_match()

        self.another_match.match_url = self.match.match_url
        result = self.repository.insert_match(self.another_match)
        self.assertFalse(
            result,
            f"Am putut insera doua meciuri cu acelasi url"
        )

    def test_matches_same_teams(self):
        self.match.away_team = self.match.home_team
        result = self.helper_insert_teams_and_match()

        self.assertFalse(
            result,
            f"Am putut insera un meci cu aceleasi echipe"
        )

    def test_matches_get_match_by_id(self):
        self.helper_insert_teams_and_match()
        match = self.repository.get_match_by_id(self.match.mid)

        self.assertIsNotNone(match, "A fost returnat None")
        self.assertIsInstance(match, Match, "A fost returnat tipul de data gresit")
        self.assertEqual(match, self.match, "Nu a returnat echipa corecta")

    def test_matches_get_match_by_details(self):
        self.helper_insert_teams_and_match()
        result = self.repository.insert_match(self.another_match)
        self.assertFalse(result)

        match = self.repository.get_match_by_details(self.match.home_team, self.match.away_team, self.match.start_time)
        self.assertIsNotNone(match, "A fost returnat None")
        self.assertIsInstance(match, Match, "A fost returnat tipul de data gresit")
        self.assertEqual(match, self.match, "Nu a returnat echipa corecta")

    def test_matches_delete_by_id(self):
        self.helper_insert_teams_and_match()

        result = self.repository.delete_match_by_id(self.match.mid)
        self.assertTrue(
            result,
        "Nu a fost efectuate cu succes stergerea unui meci "
        )

        result = self.repository.get_match_by_id(self.match.mid)
        self.assertIsNone(
            result,
            "A fost returnat un meci"
        )

if __name__ == "__main__":
    unittest.main()
