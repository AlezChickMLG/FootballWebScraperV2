from dataclasses import dataclass

@dataclass
class Match:
    mid: str
    home_team: str
    away_team: str
    start_time: str
    match_url: str
    match_score: str