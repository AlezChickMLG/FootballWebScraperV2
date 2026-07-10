from dataclasses import dataclass

@dataclass(frozen=True)
class TeamFrozen:
    team_id: str
    team_name: str
    url: str