from dataclasses import dataclass

@dataclass
class Team:
    team_id: str
    team_name: str=''
    url: str=''
    image_url: str=''