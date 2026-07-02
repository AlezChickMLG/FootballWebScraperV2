from dataclasses import dataclass

@dataclass
class TopStatisticsObject:
    mid: str
    team_id: str
    xG: float
    posesie_minge: int
    total_suturi: int
    suturi_pe_poarta: int
    ocazii_mari: int
    cornere: int
    pase_procentaj: int
    pase_reusite: int
    pase_totale: int
    cartonase_galbene: int
    cartonase_rosii: int