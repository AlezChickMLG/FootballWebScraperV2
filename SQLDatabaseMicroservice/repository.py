import sqlite3

from football_dataclasses.aparare_dataclass import AparareObject
from football_dataclasses.atac_dataclass import AtacObject
from football_dataclasses.matches_dataclass import Match
from football_dataclasses.pase_dataclass import PaseObject
from football_dataclasses.portar_dataclass import PortarObject
from football_dataclasses.suturi_dataclass import SuturiObject
from football_dataclasses.teams_dataclass import Team
from football_dataclasses.topStatistics_dataclass import TopStatisticsObject


class Repository:
    def __init__(self, database_name="football_database"):
        self.database_connection = sqlite3.connect(database_name)
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
                start_time TEXT,
                match_url TEXT NOT NULL,
                match_score TEXT NOT NULL,
                
                CHECK (home_team != away_team),
                UNIQUE(home_team, away_team, start_time),
                UNIQUE(match_url),
                FOREIGN KEY (home_team) REFERENCES Teams(team_id),
                FOREIGN KEY (away_team) REFERENCES Teams(team_id)
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
                FOREIGN KEY (mid) REFERENCES Matches(mid),
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
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
                FOREIGN KEY (mid) REFERENCES Matches(mid),
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
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
                FOREIGN KEY (mid) REFERENCES Matches(mid),
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
            );
        ''')
        print("Am creat tabela de aparare")

    def create_table_pase(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pase (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
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
                FOREIGN KEY (mid) REFERENCES Matches(mid),
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
            )
        ''')
        print("Am creat tabela de pase")

    def create_table_atac(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Atac (
                mid TEXT NOT NULL,
                team_id TEXT NOT NULL,
                atingeri_in_careul_advers INTEGER,
                pase_filtrante_reusite INTEGER,
                ofsaiduri INTEGER,
                lovituri_libere INTEGER,
                
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid),
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
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
                
                PRIMARY KEY (mid, team_id),
                FOREIGN KEY (mid) REFERENCES Matches(mid),
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
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
                                INSERT INTO Teams (team_id, team_name, url)
                                VALUES (?, ?, ?)
                                """, (
                                    team.team_id,
                                    team.team_name,
                                    team.url
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
                    match_score
                ) VALUES (
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
                match.match_score
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
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    pase.mid,
                                    pase.team_id,
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
                                                  atingeri_in_careul_advers,
                                                  pase_filtrante_reusite,
                                                  ofsaiduri,
                                                  lovituri_libere)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    atac.mid,
                                    atac.team_id,
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
                                                     goluri_prevenite)
                                VALUES (?, ?, ?, ?, ?)
                                """, (
                                    portar.mid,
                                    portar.team_id,
                                    portar.interventii_portar,
                                    portar.xGOT_impotriva,
                                    portar.goluri_prevenite
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

            return Team(*self.cursor.fetchone())
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

            return Team(*self.cursor.fetchone())
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

            return Match(*self.cursor.fetchone())
        except Exception as e:
            print(f"Eroare la gasirea meciului dupa id: {mid}")
            return None

    def get_match_by_details(self, home_team, away_team, start_time):
        try:
            self.cursor.execute('''
                SELECT * FROM Matches 
                WHERE home_team = ?
                AND away_team = ?
                AND start_time = ?
            ''', (
                home_team,
                away_team,
                start_time
            ))

            return Match(*self.cursor.fetchone())
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

            return TopStatisticsObject(*self.cursor.fetchone())
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

            return SuturiObject(*self.cursor.fetchone())
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

            return PaseObject(*self.cursor.fetchone())
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

            return AparareObject(*self.cursor.fetchone())
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

            return AtacObject(*self.cursor.fetchone())
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

            return PortarObject(*self.cursor.fetchone())
        except Exception as e:
            print(f"Eroare la gasirea portari dupa id: {e}")
    '''FUNCTII DE SELECT'''

if __name__ == "__main__":
    repository = Repository()