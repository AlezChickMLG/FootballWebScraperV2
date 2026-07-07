from dataclasses import dataclass

@dataclass
class PaseObject:
    mid: str
    team_id: str
    pase_procentaj: int=-1
    pase_reusite: int=-1
    pase_totale: int=-1
    pase_lungi_procentaj: int=-1
    pase_lungi_reusite: int=-1
    pase_lungi_totale: int=-1
    pase_in_treimea_finala_procentaj: int=-1
    pase_in_treimea_finala_reusite: int=-1
    pase_in_treimea_finala_totale: int=-1
    centrari_procentaj: int=-1
    centrari_reusite: int=-1
    centrari_totale: int=-1
    xA: float=-1
    aruncari_de_la_margine: int=-1