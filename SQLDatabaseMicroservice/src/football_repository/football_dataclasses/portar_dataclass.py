from dataclasses import dataclass

@dataclass
class PortarObject:
    mid: str
    team_id: str
    interventii_portar: int=-1
    xGOT_impotriva: float=-1
    goluri_prevenite: float=-1
    aut_de_poarta: int=-1