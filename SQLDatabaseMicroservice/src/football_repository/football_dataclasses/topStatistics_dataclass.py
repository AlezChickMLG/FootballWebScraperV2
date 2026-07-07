from dataclasses import dataclass

@dataclass
class TopStatisticsObject:
    mid: str
    team_id: str
    xG: float=-1
    posesie_minge: int=-1
    total_suturi: int=-1
    suturi_pe_poarta: int=-1
    ocazii_mari: int=-1
    cornere: int=-1
    pase_procentaj: int=-1
    pase_reusite: int=-1
    pase_totale: int=-1
    cartonase_galbene: int=-1
    cartonase_rosii: int=-1