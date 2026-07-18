import unittest

from football_repository.football_dataclasses.competition_dataclass import Competition
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.repository import Repository

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

class TestCompetition(unittest.TestCase):
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

        self.competition = Competition(
            id="c123",
            country="Romania",
            competition_name="Superliga",
            url="fotbal/superliga"
        )

        self.match = Match(
            mid="123",
            home_team="abcdef",
            away_team="xyz",
            start_time="maine la pranz",
            match_url="facebuci.ro",
            match_score="0:3",
            is_played=False,
            competition_id="c123"
        )

    def helper_insert(self):
        self.assertTrue(self.repository.insert_team(self.team))
        self.assertTrue(self.repository.insert_team(self.another_team))
        self.assertTrue(self.repository.insert_match(self.match))

    def test_insert_competition(self):
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

    def test_insert_other_competition(self):
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

        self.competition.id = "c12345"
        self.competition.competition_name = "Premier league"
        self.competition.url = "fotbal/premier-league"
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to update competition"
        )

    def test_fail_to_add_competitions(self):
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

        self.competition.id = "c123"
        self.competition.competition_name = "Premier league"
        self.competition.url = "fotbal/premier-league"

        self.assertFalse(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

        self.competition.id = "c12345"
        self.competition.competition_name = "Superliga"
        self.competition.url = "fotbal/superliga123"

        self.assertFalse(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

    def test_update_competition(self):
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )


        self.competition.id = "c123"
        self.competition.competition_name = "Premier league"
        self.competition.url = "fotbal/premier-league"
        self.assertTrue(
            self.repository.update_competition(self.competition),
            f"Error: failed to update competition"
        )

    def test_get_competition_by_id(self):
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

        competition = self.repository.get_competition_by_id(self.competition.id)

        self.assertIsNotNone(
            competition,
            f"Error: none competition"
        )

        self.assertIsInstance(
            competition,
            Competition,
            f"Error: different instance"
        )

    def test_get_competition_by_name(self):
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

        competition = self.repository.get_competition_by_name(self.competition.competition_name)

        self.assertIsNotNone(
            competition,
            f"Error: none competition"
        )

        self.assertIsInstance(
            competition,
            Competition,
            f"Error: different instance"
        )

    def test_delete_competition(self):
        self.assertTrue(
            self.repository.insert_competition(self.competition),
            f"Error: failed to insert competition"
        )

        self.assertTrue(
            self.repository.delete_team_by_id(self.competition.id),
            f"Error: failed to delete competition"
        )


if __name__ == '__main__':
    unittest.main()
