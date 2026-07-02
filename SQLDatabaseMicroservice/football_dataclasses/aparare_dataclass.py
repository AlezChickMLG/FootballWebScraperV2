from dataclasses import dataclass

@dataclass
class AparareObject:
    mid: str
    team_id: str
    faulturi: int
    deposedari_procentaj: int
    deposedari_reusite: int
    deposedari_totale: int
    dueluri_castigate: int
    respingeri: int
    interceptii: int
    erori_sut: int
    erori_gol: int