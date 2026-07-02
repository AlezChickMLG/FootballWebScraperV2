from dataclasses import dataclass

@dataclass
class PortarObject:
    mid: str
    team_id: str
    interventii_portar: int
    xGOT_impotriva: float
    goluri_prevenite: float