from dataclasses import dataclass

@dataclass
class AparareObject:
    mid: str
    team_id: str
    faulturi: int=-1
    deposedari_procentaj: int=-1
    deposedari_reusite: int=-1
    deposedari_totale: int=-1
    dueluri_castigate: int=-1
    respingeri: int=-1
    interceptii: int=-1
    erori_sut: int=-1
    erori_gol: int=-1