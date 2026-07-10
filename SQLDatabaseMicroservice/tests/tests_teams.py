import unittest

from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.repository import Repository


class TestsTeams(unittest.TestCase):
    def setUp(self):
        self.repository = Repository(":memory:")

        self.team = Team(
            team_id="abcdef",
            team_name="Mexic",
            url="some_url",
            image_url="alabala.portocala"
        )

        self.another_team = Team(
            team_id="xyz",
            team_name="Canada",
            url="another_url"
        )

    def tearDown(self):
        self.repository.database_connection.close()

    def test_insert_team_correct(self):
        self.assertTrue(
            self.repository.insert_team(self.team),
            f"Eroare la inserarea echipei"
        )

        self.repository.cursor.execute("SELECT * FROM Teams")
        result = self.repository.cursor.fetchone()

        self.assertIsNotNone(
            result,
            "Nu a fost gasita echipa in tabela"
        )

    def test_team_unique_team_id(self):
        result = self.repository.insert_team(self.team)
        self.assertTrue(
            result,
            f"Eroare la inserarea primei echipe"
        )

        self.another_team.team_id = "abcdef"
        result = self.repository.insert_team(self.another_team)
        self.assertFalse(
            result,
            f"A esuat constrangerea de unicitate team_id"
        )

    def test_team_unique_team_name(self):
        result = self.repository.insert_team(self.team)
        self.assertTrue(
            result,
            f"Eroare la inserarea primei echipe"
        )

        self.another_team.team_name = "Mexic"

        result = self.repository.insert_team(self.another_team)
        self.assertFalse(
            result,
            f"A esuat constrangerea de unicitate team_name"
        )

    def test_team_unique_team_url(self):
        result = self.repository.insert_team(self.team)
        self.assertTrue(
            result,
            f"Eroare la inserarea primei echipe"
        )

        self.another_team.url = "some_url"

        result = self.repository.insert_team(self.another_team)
        self.assertFalse(
            result,
            f"A esuat constrangerea de unicitate url"
        )

    def test_team_get_team_by_name(self):
        self.repository.insert_team(self.team)
        team = self.repository.get_team_by_name(self.team.team_name)

        self.assertIsNotNone(team, "A fost returnat None")
        self.assertIsInstance(team, Team, "A fost returnat tipul de data gresit")
        self.assertEqual(team, self.team, "Nu a returnat echipa corecta")

    def test_team_get_team_by_id(self):
        self.repository.insert_team(self.team)
        team = self.repository.get_team_by_id(self.team.team_id)

        self.assertIsNotNone(team, "A fost returnat None")
        self.assertIsInstance(team, Team, "A fost returnat tipul de data gresit")
        self.assertEqual(team, self.team, "Nu a returnat echipa corecta")

    def test_team_delete_by_id(self):
        self.repository.insert_team(self.team)

        result = self.repository.delete_team_by_id(self.team.team_id)
        self.assertTrue(
            result,
            "Nu s-a efectuat corect stergerea unei echipe"
        )

        result = self.repository.get_team_by_id(self.team.team_id)
        self.assertIsNone(
            result,
            "A returnat un obiect desi nu trebuia"
        )

    def test_update(self):
        self.repository.insert_team(self.team)

        self.team.team_name = "Germania"
        result = self.repository.update_team(self.team)
        self.assertTrue(
            result,
            "Update eronat"
        )

        result = self.repository.get_team_by_id(team_id=self.team.team_id)
        self.assertEqual(
            result,
            self.team,
            "Echipe diferite"
        )

    def test_update_few_fields(self):
        self.repository.insert_team(self.team)

        new_team = Team(
            team_id=self.team.team_id,
            team_name="Germania",
            url="instabuci.ro"
        )

        result = self.repository.update_team(new_team)
        self.assertTrue(
            result,
            "Update eronat"
        )

        result = self.repository.get_team_by_id(team_id=self.team.team_id)
        self.assertEqual(
            result.team_id,
            self.team.team_id,
            "Echipe diferite"
        )
        self.assertEqual(
            result.team_name,
            new_team.team_name,
            "Nume diferite"
        )
        self.assertEqual(
            result.url,
            new_team.url,
            "URL-uri diferite"
        )


if __name__ == "__main__":
    unittest.main()