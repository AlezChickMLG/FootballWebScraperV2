from dataclasses import dataclass

@dataclass(frozen=True)
class MatchFrozen:
    mid: str
    home_team: str
    away_team: str
    start_time: str
    match_url: str
    match_score: str
    is_played: int = 1