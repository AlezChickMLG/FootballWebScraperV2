import unittest
from src.football_proxy.data_processors.StatisticsSerializer import StatisticsSerializer
from src.football_proxy.proxy import Proxy

class StatisticsSerializerTest(unittest.TestCase):
    def setUp(self):
        self.statistics_serializer = StatisticsSerializer()
        self.proxy = Proxy(headless=False, database_name=":memory:")

    def test_statistics_serializer(self):
        try:
            team = self.proxy.get_team("Anglia")
            matches = self.proxy.get_matches(team_name=team.team_name, team_id=team.team_id)
            statistics = self.proxy.get_match_statistics(matches[0])

            serialized_statistics = self.statistics_serializer.serialize_statistics(statistics)

            self.assertIsNotNone(serialized_statistics, "statistici goale")
            self.assertIsInstance(serialized_statistics, dict, "Colectie gresita")

        except Exception as e:
            print(f"Error: {e}")
if __name__ == '__main__':
    unittest.main()
