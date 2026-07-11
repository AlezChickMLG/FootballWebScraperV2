import sqlite3
from dataclasses import fields

from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject


class Repository:
    def __init__(self, database_name="football_database"):
        self.database_connection = sqlite3.connect(database_name, check_same_thread=False)
        self.database_connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.database_connection.cursor()
        self.create_all_tables()

    def commit(self):
        self.database_connection.commit()
        print("Am dat commit")

    '''FUNCTII DE CREAT TABELE'''
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
        print("Am creat tabela de echipe")

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
                
                CHECK (home_team != away_team),
                CHECK (is_played IN (0, 1)),
                
                UNIQUE(home_team, away_team, start_time),
                UNIQUE(match_url),
                
                FOREIGN KEY (home_team) REFERENCES Teams(team_id)
                ON DELETE CASCADE,
                
                FOREIGN KEY (away_team) REFERENCES Teams(team_id)
                ON DELETE CASCADE
            )
        ''')
        print("Am creat tabela de meciuri")

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
                
                FOREIGN KEY (mid) REFERENCES Matches(mid)
                ON DELETE CASCADE,
                
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                ON DELETE CASCADE
            );
        ''')
        print("Am creat tabela de top statistici")

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
                
                FOREIGN KEY (mid) REFERENCES Matches(mid)
                ON DELETE CASCADE, 
                
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                ON DELETE CASCADE
            );
        ''')
        print("Am creat tabela de suturi")

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
                
                FOREIGN KEY (mid) REFERENCES Matches(mid)
                ON DELETE CASCADE, 
                
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                ON DELETE CASCADE
            );
        ''')
        print("Am creat tabela de aparare")

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
                
                FOREIGN KEY (mid) REFERENCES Matches(mid)
                ON DELETE CASCADE,
                 
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                ON DELETE CASCADE
            )
        ''')
        print("Am creat tabela de pase")

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
                
                FOREIGN KEY (mid) REFERENCES Matches(mid)
                ON DELETE CASCADE, 
                
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                ON DELETE CASCADE
            );
        ''')
        print("Am creat tabela de atac")

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
                
                FOREIGN KEY (mid) REFERENCES Matches(mid)
                ON DELETE CASCADE, 
                
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
                ON DELETE CASCADE
            );
        ''')
        print("Am creat tabela de portari")

    def create_all_statistics_tables(self):
        self.create_table_top_statistics()
        self.create_table_suturi()
        self.create_table_pase()
        self.create_table_aparare()
        self.create_table_atac()
        self.create_table_portari()

        print("Am creat toate tabelele de statistici")

    def create_all_tables(self):
        self.create_table_teams()
        self.create_table_matches()
        self.create_all_statistics_tables()

        print("Am creat toate tabelele")
    '''FUNCTII DE CREAT TABELE'''

    '''FUNCTII DE INSERARE'''
    def insert_team(self, team: Team):
        try:
            self.cursor.execute("""
                                INSERT INTO Teams (team_id, team_name, url, image_url)
                                VALUES (?, ?, ?, ?)
                                """, (
                                    team.team_id,
                                    team.team_name,
                                    team.url,
                                    team.image_url
                                ))

            print("Am introdus un obiect in tabela teams")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unei echipe in tabela teams: {e}")
            return False

    def insert_match(self, match: Match):
        try:

            self.cursor.execute('''
                INSERT INTO Matches (
                    mid, 
                    home_team,
                    away_team, 
                    start_time,
                    match_url,
                    match_score,
                    is_played
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                         )
            ''', (
                match.mid,
                match.home_team,
                match.away_team,
                match.start_time,
                match.match_url,
                match.match_score,
                1 if match.is_played else 0
            ))

            print("Am introdus un obiect in tabela matches")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unui mechi in tabela matches: {e}")
            return False

    def insert_top_statistic(self, statistics: TopStatisticsObject):
        try:
            self.cursor.execute("""
                                INSERT INTO TopStatistics (mid,
                                                           team_id,
                                                           xG,
                                                           posesie_minge,
                                                           total_suturi,
                                                           suturi_pe_poarta,
                                                           ocazii_mari,
                                                           cornere,
                                                           pase_procentaj,
                                                           pase_reusite,
                                                           pase_totale,
                                                           cartonase_galbene,
                                                           cartonase_rosii)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    statistics.mid,
                                    statistics.team_id,
                                    statistics.xG,
                                    statistics.posesie_minge,
                                    statistics.total_suturi,
                                    statistics.suturi_pe_poarta,
                                    statistics.ocazii_mari,
                                    statistics.cornere,
                                    statistics.pase_procentaj,
                                    statistics.pase_reusite,
                                    statistics.pase_totale,
                                    statistics.cartonase_galbene,
                                    statistics.cartonase_rosii
                                ))
            print("Am introdus un obiect in tabela top statistici")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unui obiect in tabela top statistics: {e}")
            return False

    def insert_suturi(self, suturi: SuturiObject):
        try:
            self.cursor.execute("""
                                INSERT INTO Suturi (mid,
                                                    team_id,
                                                    xG,
                                                    xGOT,
                                                    total_suturi,
                                                    suturi_pe_poarta,
                                                    suturi_pe_langa_poarta,
                                                    suturi_blocate,
                                                    suturi_din_interiorul_careului,
                                                    suturi_din_afara_careului,
                                                    bare,
                                                    goluri_marcate_cu_capul)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    suturi.mid,
                                    suturi.team_id,
                                    suturi.xG,
                                    suturi.xGOT,
                                    suturi.total_suturi,
                                    suturi.suturi_pe_poarta,
                                    suturi.suturi_pe_langa_poarta,
                                    suturi.suturi_blocate,
                                    suturi.suturi_din_interiorul_careului,
                                    suturi.suturi_din_afara_careului,
                                    suturi.bare,
                                    suturi.goluri_marcate_cu_capul
                                ))
            print("Am introdus un obiect in tabela suturi")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unui obiect in tabela suturi: {e}")
            return False

    def insert_pase(self, pase: PaseObject):
        try:
            self.cursor.execute("""
                                INSERT INTO Pase (mid,
                                                  team_id,
                                                  pase_procentaj,
                                                  pase_reusite,
                                                  pase_totale,
                                                  pase_lungi_procentaj,
                                                  pase_lungi_reusite,
                                                  pase_lungi_totale,
                                                  pase_in_treimea_finala_procentaj,
                                                  pase_in_treimea_finala_reusite,
                                                  pase_in_treimea_finala_totale,
                                                  centrari_procentaj,
                                                  centrari_reusite,
                                                  centrari_totale,
                                                  xA,
                                                  aruncari_de_la_margine)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    pase.mid,
                                    pase.team_id,
                                    pase.pase_procentaj,
                                    pase.pase_reusite,
                                    pase.pase_totale,
                                    pase.pase_lungi_procentaj,
                                    pase.pase_lungi_reusite,
                                    pase.pase_lungi_totale,
                                    pase.pase_in_treimea_finala_procentaj,
                                    pase.pase_in_treimea_finala_reusite,
                                    pase.pase_in_treimea_finala_totale,
                                    pase.centrari_procentaj,
                                    pase.centrari_reusite,
                                    pase.centrari_totale,
                                    pase.xA,
                                    pase.aruncari_de_la_margine
                                ))

            print("Am introdus un obiect in tabela pase")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unui obiect in tabela Pase: {e}")
            return False

    def insert_aparare(self, aparare: AparareObject):
        try:
            self.cursor.execute("""
                                INSERT INTO Aparare (mid,
                                                     team_id,
                                                     faulturi,
                                                     deposedari_procentaj,
                                                     deposedari_reusite,
                                                     deposedari_totale,
                                                     dueluri_castigate,
                                                     respingeri,
                                                     interceptii,
                                                     erori_sut,
                                                     erori_gol)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    aparare.mid,
                                    aparare.team_id,
                                    aparare.faulturi,
                                    aparare.deposedari_procentaj,
                                    aparare.deposedari_reusite,
                                    aparare.deposedari_totale,
                                    aparare.dueluri_castigate,
                                    aparare.respingeri,
                                    aparare.interceptii,
                                    aparare.erori_sut,
                                    aparare.erori_gol
                                ))
            print("Am introdus un obiect in tabela aparare")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unui obiect in tabela Aparare")
            return False

    def insert_atac(self, atac: AtacObject):
        try:
            self.cursor.execute("""
                                INSERT INTO Atac (mid,
                                                  team_id,
                                                  ocazii_mari,
                                                  cornere,
                                                  atingeri_in_careul_advers,
                                                  pase_filtrante_reusite,
                                                  ofsaiduri,
                                                  lovituri_libere)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    atac.mid,
                                    atac.team_id,
                                    atac.ocazii_mari,
                                    atac.cornere,
                                    atac.atingeri_in_careul_advers,
                                    atac.pase_filtrante_reusite,
                                    atac.ofsaiduri,
                                    atac.lovituri_libere
                                ))
            print("Am introdus un obiect in tabela atac")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unui obiect in tabela atac: {e}")
            return False

    def insert_portar(self, portar: PortarObject):
        try:
            self.cursor.execute("""
                                INSERT INTO Portari (mid,
                                                     team_id,
                                                     interventii_portar,
                                                     xGOT_impotriva,
                                                     goluri_prevenite,
                                                     aut_de_poarta)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    portar.mid,
                                    portar.team_id,
                                    portar.interventii_portar,
                                    portar.xGOT_impotriva,
                                    portar.goluri_prevenite,
                                    portar.aut_de_poarta
                                ))

            print("Am introdus un obiect in tabela portar")
            return True

        except Exception as e:
            print(f"Eroare la adaugarea unui obeiect in tabela portari: {e}")
            return False
    '''FUNCTII DE INSERARE'''

    '''FUNCTII DE SELECT'''
    def get_team_by_name(self, name):
        try:
            self.cursor.execute('''
                SELECT * FROM Teams 
                WHERE team_name = ?
            ''', (
                name,
            ))

            result = self.cursor.fetchone()
            return Team(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea echipei dupa nume: {name}: {e}")
            return None

    def get_team_by_id(self, team_id):
        try:
            self.cursor.execute('''
                SELECT * FROM Teams 
                WHERE team_id = ?
            ''', (
                team_id,
            ))

            result = self.cursor.fetchone()
            return Team(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea echipei dupa id: {team_id}")
            return None

    def get_match_by_id(self, mid):
        try:
            self.cursor.execute('''
                SELECT * FROM Matches 
                WHERE mid = ?
            ''', (
                mid,
            ))

            result = self.cursor.fetchone()
            return Match(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea meciului dupa id: {mid}")
            return None

    def get_match_by_details(self, home_team=None, away_team=None, start_time=None):
        try:
            conditions = []
            parameters = []

            if home_team:
                conditions.append("home_team = ?")
                parameters.append(home_team)

            if away_team:
                conditions.append("away_team = ?")
                parameters.append(away_team)

            if start_time:
                conditions.append("start_time = ?")
                parameters.append(start_time)

            if not conditions:
                return None

            sql = f"SELECT * FROM Matches WHERE {' AND '.join(conditions)}"

            self.cursor.execute(sql, parameters)

            result = self.cursor.fetchall()
            return list(Match(*match) for match in result) if result else None

        except Exception as e:
            print(f"Eroare la gasirea meciului dupa echipe si timpul de start: {e}")
            return None
    def get_matches_by_is_played(self, is_played=True):
        try:
            sql = '''SELECT * FROM Matches
                  WHERE is_played = ?'''

            self.cursor.execute(sql, (
                1 if is_played else 0,
            ))

            result = self.cursor.fetchall()
            return list(Match(*match) for match in result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea meciului dupa echipe si timpul de start: {e}")
            return None


    def get_top_statistics_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                SELECT * FROM TopStatistics
                WHERE mid = ?
                AND team_id = ?
            ''', (
                mid,
                team_id
            ))

            result = self.cursor.fetchone()
            return TopStatisticsObject(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea top statisticilor dupa id: {e}")

    def get_suturi_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                SELECT * FROM Suturi
                WHERE mid = ?
                AND team_id = ?
            ''', (
                mid,
                team_id
            ))

            result = self.cursor.fetchone()
            return SuturiObject(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea suturi dupa id: {e}")

    def get_pase_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                SELECT * FROM Pase
                WHERE mid = ?
                AND team_id = ?
            ''', (
                mid,
                team_id
            ))

            result = self.cursor.fetchone()
            return PaseObject(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea pase dupa id: {e}")

    def get_aparare_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                SELECT * FROM Aparare
                WHERE mid = ?
                AND team_id = ?
            ''', (
                mid,
                team_id
            ))

            result = self.cursor.fetchone()
            return AparareObject(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea aparare dupa id: {e}")

    def get_atac_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                SELECT * FROM Atac
                WHERE mid = ?
                AND team_id = ?
            ''', (
                mid,
                team_id
            ))

            result = self.cursor.fetchone()
            return AtacObject(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea atac dupa id: {e}")

    def get_portari_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                SELECT * FROM Portari
                WHERE mid = ?
                AND team_id = ?
            ''', (
                mid,
                team_id
            ))

            result = self.cursor.fetchone()
            return PortarObject(*result) if result else None
        except Exception as e:
            print(f"Eroare la gasirea portari dupa id: {e}")
    '''FUNCTII DE SELECT'''

    '''FUNCTII DE DELETE'''
    def delete_team_by_id(self, team_id):
        try:
            self.cursor.execute('''
                DELETE FROM Teams 
                    WHERE team_id = ?
            ''', (
                team_id,
            ))
            print(f"Am sters echipa {team_id}")
            return True

        except Exception as e:
            print(f"Eroare la stergerea unei echipe: {e}")
            return False

    def delete_match_by_id(self, mid):
        try:
            self.cursor.execute('''
                DELETE FROM Matches 
                    WHERE mid = ?
            ''', (
                mid,
            ))
            print(f"Am sters meciul: {mid}")
            return True
        except Exception as e:
            print(f"Eroare la stergerea unui meci: {e}")
            return False

    def delete_top_statistics_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                DELETE FROM TopStatistics
                    WHERE mid = ?
                    AND team_id = ?
            ''', (
                mid,
                team_id
            ))
            print(f"Am sters un rand din top_statistics: mid: {mid}, team_id: {team_id}")
            return True
        except Exception as e:
            print(f"Eroare la stergerea unui rand din top_statistics: {e}")
            return False

    def delete_suturi_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                                DELETE
                                FROM Suturi
                                WHERE mid = ?
                                  AND team_id = ?
                                ''', (
                                    mid,
                                    team_id
                                ))
            print(f"Am sters un rand din suturi: mid: {mid}, team_id: {team_id}")
            return True
        except Exception as e:
            print(f"Eroare la stergerea unui rand din suturi: {e}")
            return False

    def delete_pase_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                                DELETE
                                FROM Pase
                                WHERE mid = ?
                                  AND team_id = ?
                                ''', (
                                    mid,
                                    team_id
                                ))
            print(f"Am sters un rand din pase: mid: {mid}, team_id: {team_id}")
            return True
        except Exception as e:
            print(f"Eroare la stergerea unui rand din pase: {e}")
            return False

    def delete_atac_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                                DELETE
                                FROM Atac
                                WHERE mid = ?
                                  AND team_id = ?
                                ''', (
                                    mid,
                                    team_id
                                ))
            print(f"Am sters un rand din atac: mid: {mid}, team_id: {team_id}")
            return True
        except Exception as e:
            print(f"Eroare la stergerea unui rand din atac: {e}")
            return False

    def delete_aparare_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                                DELETE
                                FROM Aparare
                                WHERE mid = ?
                                  AND team_id = ?
                                ''', (
                                    mid,
                                    team_id
                                ))
            print(f"Am sters un rand din aparare: mid: {mid}, team_id: {team_id}")
            return True
        except Exception as e:
            print(f"Eroare la stergerea unui rand din aparare: {e}")
            return False

    def delete_portari_by_id(self, mid, team_id):
        try:
            self.cursor.execute('''
                                DELETE
                                FROM Portari
                                WHERE mid = ?
                                  AND team_id = ?
                                ''', (
                                    mid,
                                    team_id
                                ))
            print(f"Am sters un rand din portari: mid: {mid}, team_id: {team_id}")
            return True
        except Exception as e:
            print(f"Eroare la stergerea unui rand din portari: {e}")
            return False

    '''UPDATE'''
    def _update(self, object_to_be_updated, id_name, id_value, tabel_name):
        try:
            sql = f"UPDATE {tabel_name} SET "
            updated_fields = []
            parameters = []

            for field in fields(object_to_be_updated):
                field_value = getattr(object_to_be_updated, field.name)
                if (field.type == str and field_value != '') or (field.type in (int, float) and field_value != -1):
                    updated_fields.append(f"{field.name} = ?")
                    parameters.append(field_value)


            sql += ', '.join(updated_fields)
            if not isinstance(id_name, list):
                sql += f" WHERE {id_name} = ?"
                self.cursor.execute(sql, (*parameters, id_value))

            else:
                sql += f"WHERE " + " AND ".join(f"{pk} = ?" for pk in id_name)
                self.cursor.execute(sql, (*parameters, *id_value))

            return True

        except Exception as e:
            print(f"Eroare la actualizarea tabelei {tabel_name} - id {id_value}: {e}")
            return False

    def update_team(self, team: Team):
        return self._update(object_to_be_updated=team, id_name="team_id", id_value=team.team_id, tabel_name="Teams")

    def update_match(self, match: Match):
        return self._update(object_to_be_updated=match, id_name="mid", id_value=match.mid, tabel_name="Matches")

    def update_top_statistics(self, top_statistics: TopStatisticsObject):
        return self._update(object_to_be_updated=top_statistics, id_name=["team_id", "mid"],
                            id_value=[top_statistics.team_id, top_statistics.mid], tabel_name="TopStatistics")

    def update_suturi(self, suturi: SuturiObject):
        return self._update(object_to_be_updated=suturi, id_name=["team_id", "mid"],
                            id_value=[suturi.team_id, suturi.mid], tabel_name="Suturi")

    def update_atac(self, atac: AtacObject):
        return self._update(object_to_be_updated=atac, id_name=["team_id", "mid"],
                            id_value=[atac.team_id, atac.mid], tabel_name="Atac")

    def update_pase(self, pase: PaseObject):
        return self._update(object_to_be_updated=pase, id_name=["team_id", "mid"],
                            id_value=[pase.team_id, pase.mid], tabel_name="Pase")
    
    def update_aparare(self, aparare: AparareObject):
        return self._update(object_to_be_updated=aparare, id_name=["team_id", "mid"],
                            id_value=[aparare.team_id, aparare.mid], tabel_name="Aparare")

    def update_portar(self, portar: PortarObject):
        return self._update(object_to_be_updated=portar, id_name=["team_id", "mid"],
                            id_value=[portar.team_id, portar.mid], tabel_name="Portari")

if __name__ == "__main__":
    repository = Repository()