import unittest
from unittest.mock import patch

from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.teams_dataclass import Team

from app import app

class TestFlask(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    @patch("app.proxy")
    def test_get_matches(self, mock_proxy):
        mock_proxy.get_team.return_value = Team(team_id="123")
        mock_proxy.get_matches.return_value = [Match(mid="123"), Match(mid="456")]

        response = self.client.get("/get_matches/Spania")
        self.assertEqual(response.status_code, 200, "Status code diferit")


if __name__ == '__main__':
    unittest.main()
