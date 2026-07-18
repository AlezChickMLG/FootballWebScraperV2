from dataclasses import dataclass

@dataclass
class Competition:
    id: str
    country: str
    competition_name: str
    url: str
    competition_image_url: str=''
