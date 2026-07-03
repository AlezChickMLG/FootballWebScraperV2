import unittest
from football_repository.repository import Repository


class TestsTables(unittest.TestCase):
    def setUp(self):
        self.repository = Repository(":memory:")

    def tearDown(self):
        self.repository.database_connection.close()

    def helper_exists_table(self, name):
        self.repository.cursor.execute('''
               SELECT name
               FROM sqlite_master
               WHERE type = 'table'
                AND name = ?
           ''', (
                name,
           ))

        return True if self.repository.cursor.fetchone() is not None else False

    def test_created_tables(self):
        all_tables = ["Teams", "Matches", "TopStatistics", "Suturi", "Pase",
                      "Aparare", "Atac", "Portari"]

        for table in all_tables:
            self.assertTrue(
                self.helper_exists_table(table),
                f"Tabelul {table} nu a fost creat cu succes"
            )

if __name__ == "__main__":
    unittest.main()