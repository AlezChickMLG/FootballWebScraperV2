import sqlite3
import logging
from dataclasses import fields

from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.competition_dataclass import Competition
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject

logger = logging.getLogger(__name__)

# Sentinel values that mean "field not set" — mirror the dataclass defaults.
# A str field left as "" or a numeric field left as -1 is treated as absent
# during partial updates (only set fields get written to the UPDATE statement).
_EMPTY_STR = ""
_EMPTY_NUM = -1

# Maps each statistics dataclass to its table. mid/team_id composite key
# and column names all derive from the dataclass fields, so adding a stat
# column means editing only the dataclass and the CREATE TABLE below.
_STAT_TABLES = {
    TopStatisticsObject: "TopStatistics",
    SuturiObject: "Suturi",
    PaseObject: "Pase",
    AtacObject: "Atac",
    AparareObject: "Aparare",
    PortarObject: "Portari",
}


class Repository:
    def __init__(self, database_name="football_database"):
        self.database_connection = sqlite3.connect(database_name, check_same_thread=False)
        self.database_connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.database_connection.cursor()
        self.create_all_tables()

    def commit(self):
        self.database_connection.commit()

    def close(self):
        self.database_connection.close()

    # ------------------------------------------------------------------ #
    #  Generic CRUD helpers                                              #
    #  Every insert/get/delete/update below is a thin wrapper over one   #
    #  of these. Columns and values come from the dataclass fields, so   #
    #  the SQL is always in sync with the dataclass definition.          #
    # ------------------------------------------------------------------ #
    def _insert(self, obj, table_name):
        try:
            field_names = [f.name for f in fields(obj)]
            columns = ", ".join(field_names)
            placeholders = ", ".join("?" for _ in field_names)
            values = [getattr(obj, name) for name in field_names]

            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql, values)
            return True
        except Exception as e:
            logger.error("Insert into %s failed: %s", table_name, e)
            return False

    def _get_one(self, cls, table_name, where):
        """where: dict of column -> value. Returns a single dataclass or None."""
        try:
            clause = " AND ".join(f"{col} = ?" for col in where)
            sql = f"SELECT * FROM {table_name} WHERE {clause}"
            self.cursor.execute(sql, list(where.values()))
            result = self.cursor.fetchone()
            return cls(*result) if result else None
        except Exception as e:
            logger.error("Get one from %s failed: %s", table_name, e)
            return None

    def _get_many(self, cls, table_name, where=None):
        """where: optional dict of column -> value. Returns a list or None."""
        try:
            sql = f"SELECT * FROM {table_name}"
            params = []
            if where:
                clause = " AND ".join(f"{col} = ?" for col in where)
                sql += f" WHERE {clause}"
                params = list(where.values())

            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
            return [cls(*row) for row in result] if result else None
        except Exception as e:
            logger.error("Get many from %s failed: %s", table_name, e)
            return None

    def _delete(self, table_name, where):
        try:
            clause = " AND ".join(f"{col} = ?" for col in where)
            sql = f"DELETE FROM {table_name} WHERE {clause}"
            self.cursor.execute(sql, list(where.values()))
            return True
        except Exception as e:
            logger.error("Delete from %s failed: %s", table_name, e)
            return False

    def _update(self, obj, table_name, where):
        """Partial update: only fields that differ from their empty sentinel
        are written. where: dict of pk column -> value."""
        try:
            updated_fields = []
            parameters = []

            for field in fields(obj):
                if field.name in where:
                    continue
                value = getattr(obj, field.name)
                if self._is_set(value):
                    updated_fields.append(f"{field.name} = ?")
                    parameters.append(value)

            if not updated_fields:
                return False

            clause = " AND ".join(f"{col} = ?" for col in where)
            sql = f"UPDATE {table_name} SET {', '.join(updated_fields)} WHERE {clause}"
            self.cursor.execute(sql, (*parameters, *where.values()))
            return True
        except Exception as e:
            logger.error("Update %s failed: %s", table_name, e)
            return False

    @staticmethod
    def _is_set(value):
        """A field counts as 'set' if it's not the dataclass empty sentinel."""
        if isinstance(value, str):
            return value != _EMPTY_STR
        if isinstance(value, (int, float)):
            return value != _EMPTY_NUM
        return value is not None

    # ------------------------------------------------------------------ #
    #  Table creation                                                    #
    # ------------------------------------------------------------------ #
    def create_table_teams(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Teams (
                team_id TEXT PRIMARY KEY NOT NULL,
                team_name TEXT NOT NULL,
                url TEXT NOT NULL,
                image_url TEXT,

                UNIQUE(team_name),
                UNIQUE(url)
            );
        ''')

    def create_table_competition(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Competitions(
                id TEXT PRIMARY KEY NOT NULL,
                country TEXT NOT NULL,
                competition_name TEXT NOT NULL,
                url TEXT NOT NULL,
                competition_image_url TEXT NOT NULL,

                UNIQUE(competition_name),
                UNIQUE(url)
            );
        ''')

    def create_table_matches(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Matches (
                mid TEXT PRIMARY KEY NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                match_url TEXT NOT NULL,
                start_time TEXT,
                match_score TEXT NOT NULL,
                is_played INTEGER,

                competition_id TEXT,

                CHECK (home_team != away_team),
                CHECK (is_played IN (0, 1)),

                UNIQUE(home_team, away_team, start_time),
                UNIQUE(match_url),

                FOREIGN KEY (home_team) REFERENCES Teams(team_id) ON DELETE CASCADE,
                FOREIGN KEY (away_team) REFERENCES Teams(team_id) ON DELETE CASCADE,
                FOREIGN KEY (competition_id) REFERENCES Competitions(id) ON DELETE CASCADE
            );
        ''')

    def create_table_top_statistics(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TopStatistics (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
                xG REAL,
                posesie_minge INTEGER,
                total_suturi INTEGER,
                suturi_pe_poarta INTEGER,
                ocazii_mari INTEGER,
                cornere INTEGER,
                pase_procentaj INTEGER,
                pase_reusite INTEGER,
                pase_totale INTEGER,
                cartonase_galbene INTEGER,
                cartonase_rosii INTEGER,
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
            );
        ''')

    def create_table_suturi(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suturi (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
                xG REAL,
                xGOT REAL,
                total_suturi INTEGER,
                suturi_pe_poarta INTEGER,
                suturi_pe_langa_poarta INTEGER,
                suturi_blocate INTEGER,
                suturi_din_interiorul_careului INTEGER,
                suturi_din_afara_careului INTEGER,
                bare INTEGER,
                goluri_marcate_cu_capul INTEGER,
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
            );
        ''')

    def create_table_pase(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pase (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
                pase_procentaj INTEGER,
                pase_reusite INTEGER,
                pase_totale INTEGER,
                pase_lungi_procentaj INTEGER,
                pase_lungi_reusite INTEGER,
                pase_lungi_totale INTEGER,
                pase_in_treimea_finala_procentaj INTEGER,
                pase_in_treimea_finala_reusite INTEGER,
                pase_in_treimea_finala_totale INTEGER,
                centrari_procentaj INTEGER,
                centrari_reusite INTEGER,
                centrari_totale INTEGER,
                xA REAL,
                aruncari_de_la_margine INTEGER,
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
            );
        ''')

    def create_table_atac(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Atac (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
                ocazii_mari INTEGER,
                cornere INTEGER,
                atingeri_in_careul_advers INTEGER,
                pase_filtrante_reusite INTEGER,
                ofsaiduri INTEGER,
                lovituri_libere INTEGER,
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
            );
        ''')

    def create_table_portari(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Portari (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
                interventii_portar INTEGER,
                xGOT_impotriva REAL,
                goluri_prevenite REAL,
                aut_de_poarta INTEGER,
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
            );
        ''')

    def create_all_statistics_tables(self):
        self.create_table_top_statistics()
        self.create_table_suturi()
        self.create_table_pase()
        self.create_table_aparare()
        self.create_table_atac()
        self.create_table_portari()

    def create_table_aparare(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Aparare (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
                faulturi INTEGER,
                deposedari_procentaj INTEGER,
                deposedari_reusite INTEGER,
                deposedari_totale INTEGER,
                dueluri_castigate INTEGER,
                respingeri INTEGER,
                interceptii INTEGER,
                erori_sut INTEGER,
                erori_gol INTEGER,
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid) ON DELETE CASCADE,
                FOREIGN KEY (team_id) REFERENCES Teams(team_id) ON DELETE CASCADE
            );
        ''')

    def create_all_tables(self):
        self.create_table_teams()
        self.create_table_competition()
        self.create_table_matches()
        self.create_all_statistics_tables()

    # ------------------------------------------------------------------ #
    #  Insert                                                            #
    # ------------------------------------------------------------------ #
    def insert_team(self, team: Team):
        return self._insert(team, "Teams")

    def insert_competition(self, competition: Competition):
        return self._insert(competition, "Competitions")

    def insert_match(self, match: Match):
        return self._insert(match, "Matches")

    def insert_top_statistic(self, statistics: TopStatisticsObject):
        return self._insert(statistics, "TopStatistics")

    def insert_suturi(self, suturi: SuturiObject):
        return self._insert(suturi, "Suturi")

    def insert_pase(self, pase: PaseObject):
        return self._insert(pase, "Pase")

    def insert_aparare(self, aparare: AparareObject):
        return self._insert(aparare, "Aparare")

    def insert_atac(self, atac: AtacObject):
        return self._insert(atac, "Atac")

    def insert_portar(self, portar: PortarObject):
        return self._insert(portar, "Portari")

    def insert_statistic(self, statistic):
        """Insert any statistics object, dispatching on its type."""
        table = _STAT_TABLES.get(type(statistic))
        if table is None:
            logger.error("No table mapped for %s", type(statistic))
            return False
        return self._insert(statistic, table)

    # ------------------------------------------------------------------ #
    #  Select                                                            #
    # ------------------------------------------------------------------ #
    def get_team_by_name(self, name):
        return self._get_one(Team, "Teams", {"team_name": name})

    def get_team_by_id(self, team_id):
        return self._get_one(Team, "Teams", {"team_id": team_id})

    def get_competition_by_id(self, competition_id):
        return self._get_one(Competition, "Competitions", {"id": competition_id})

    def get_competition_by_name(self, competition_name):
        return self._get_one(Competition, "Competitions", {"competition_name": competition_name})

    def get_match_by_id(self, mid):
        return self._get_one(Match, "Matches", {"mid": mid})

    def get_match_by_details(self, home_team=None, away_team=None, start_time=None):
        where = {}
        if home_team:
            where["home_team"] = home_team
        if away_team:
            where["away_team"] = away_team
        if start_time:
            where["start_time"] = start_time
        if not where:
            return None
        return self._get_many(Match, "Matches", where)

    def get_matches_by_is_played(self, is_played=True):
        return self._get_many(Match, "Matches", {"is_played": 1 if is_played else 0})

    def get_top_statistics_by_id(self, mid, team_id):
        return self._get_one(TopStatisticsObject, "TopStatistics", {"mid": mid, "team_id": team_id})

    def get_suturi_by_id(self, mid, team_id):
        return self._get_one(SuturiObject, "Suturi", {"mid": mid, "team_id": team_id})

    def get_pase_by_id(self, mid, team_id):
        return self._get_one(PaseObject, "Pase", {"mid": mid, "team_id": team_id})

    def get_aparare_by_id(self, mid, team_id):
        return self._get_one(AparareObject, "Aparare", {"mid": mid, "team_id": team_id})

    def get_atac_by_id(self, mid, team_id):
        return self._get_one(AtacObject, "Atac", {"mid": mid, "team_id": team_id})

    def get_portari_by_id(self, mid, team_id):
        return self._get_one(PortarObject, "Portari", {"mid": mid, "team_id": team_id})

    # ------------------------------------------------------------------ #
    #  Delete                                                            #
    # ------------------------------------------------------------------ #
    def delete_team_by_id(self, team_id):
        return self._delete("Teams", {"team_id": team_id})

    def delete_competition_by_id(self, id):
        return self._delete("Competitions", {"id": id})

    def delete_match_by_id(self, mid):
        return self._delete("Matches", {"mid": mid})

    def delete_top_statistics_by_id(self, mid, team_id):
        return self._delete("TopStatistics", {"mid": mid, "team_id": team_id})

    def delete_suturi_by_id(self, mid, team_id):
        return self._delete("Suturi", {"mid": mid, "team_id": team_id})

    def delete_pase_by_id(self, mid, team_id):
        return self._delete("Pase", {"mid": mid, "team_id": team_id})

    def delete_atac_by_id(self, mid, team_id):
        return self._delete("Atac", {"mid": mid, "team_id": team_id})

    def delete_aparare_by_id(self, mid, team_id):
        return self._delete("Aparare", {"mid": mid, "team_id": team_id})

    def delete_portari_by_id(self, mid, team_id):
        return self._delete("Portari", {"mid": mid, "team_id": team_id})

    # ------------------------------------------------------------------ #
    #  Update                                                            #
    # ------------------------------------------------------------------ #
    def update_team(self, team: Team):
        return self._update(team, "Teams", {"team_id": team.team_id})

    def update_competition(self, competition: Competition):
        return self._update(competition, "Competitions", {"id": competition.id})

    def update_match(self, match: Match):
        return self._update(match, "Matches", {"mid": match.mid})

    def update_top_statistics(self, top_statistics: TopStatisticsObject):
        return self._update(top_statistics, "TopStatistics",
                            {"mid": top_statistics.mid, "team_id": top_statistics.team_id})

    def update_suturi(self, suturi: SuturiObject):
        return self._update(suturi, "Suturi", {"mid": suturi.mid, "team_id": suturi.team_id})

    def update_atac(self, atac: AtacObject):
        return self._update(atac, "Atac", {"mid": atac.mid, "team_id": atac.team_id})

    def update_pase(self, pase: PaseObject):
        return self._update(pase, "Pase", {"mid": pase.mid, "team_id": pase.team_id})

    def update_aparare(self, aparare: AparareObject):
        return self._update(aparare, "Aparare", {"mid": aparare.mid, "team_id": aparare.team_id})

    def update_portar(self, portar: PortarObject):
        return self._update(portar, "Portari", {"mid": portar.mid, "team_id": portar.team_id})


if __name__ == "__main__":
    repository = Repository()