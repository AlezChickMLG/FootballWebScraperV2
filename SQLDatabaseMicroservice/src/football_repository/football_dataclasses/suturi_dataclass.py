from dataclasses import dataclass

@dataclass
class SuturiObject:
    mid: str
    team_id: str
    xG: float=-1
    xGOT: float=-1
    total_suturi: int=-1
    suturi_pe_poarta: int=-1
    suturi_pe_langa_poarta: int=-1
    suturi_blocate: int=-1
    suturi_din_interiorul_careului: int=-1
    suturi_din_afara_careului: int=-1
    bare: int=-1
    goluri_marcate_cu_capul: int=-1


