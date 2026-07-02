from dataclasses import dataclass

@dataclass
class SuturiObject:
    mid: str
    team_id: str
    xG: float
    xGOT: float
    total_suturi: int
    suturi_pe_poarta: int
    suturi_pe_langa_poarta: int
    suturi_blocate: int
    suturi_din_interiorul_careului: int
    suturi_din_afara_careului: int
    bare: int
    goluri_marcate_cu_capul: int


