import unittest
from unittest.mock import patch

from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.teams_dataclass import Team

from app import app

class TestFlask(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_get_team(self):
        response = self.client.get("/get_team/Arsenal")
        self.assertTrue(response.status_code, 200)

    def test_get_matches(self):
        response = self.client.get("/get_matches/Spania")
        self.assertTrue(response.status_code, 200)

    def test_scan_matches(self):
        response = self.client.get("/scan_matches/Spania")
        self.assertTrue(response.status_code, 200)

    def test_get_statistics(self):
        response = self.client.get('/get_statistics/MHGPEKi5')
        self.assertTrue(response.status_code, 200)

    def test_get_statistics_scraper(self):
        response = self.client.get('/get_statistics/hQHtm5Ub')
        self.assertTrue(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
