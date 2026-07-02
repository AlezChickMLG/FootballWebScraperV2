from dataclasses import dataclass

@dataclass
class PaseObject:
    mid: str
    team_id: str
    pase_lungi_procentaj: int
    pase_lungi_reusite: int
    pase_lungi_totale: int
    pase_in_treimea_finala_procentaj: int
    pase_in_treimea_finala_reusite: int
    pase_in_treimea_finala_totale: int
    centrari_procentaj: int
    centrari_reusite: int
    centrari_totale: int
    xA: float
    aruncari_de_la_margine: int