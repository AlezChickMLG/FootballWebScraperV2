from dataclasses import dataclass

@dataclass
class Match:
    mid: str
    home_team: str=""
    away_team: str=""
    match_url: str=""
    start_time: str=""
    match_score: str=""
    is_played: int=1
    competition_id: str=None