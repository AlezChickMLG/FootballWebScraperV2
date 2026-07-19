import logging
from dataclasses import fields

from football_repository.football_dataclasses.competition_dataclass import Competition
from football_repository.frozen_football_dataclasses.frozen_competitions_dataclass import CompetitionFrozen

from football_scraper.NameNormalizer.NameNormalizer import NameNormalizer

from dataclasses import astuple

logger = logging.getLogger(__name__)

class CompetitionProcessor:
    _EXCEPTIONS = {
        "Meciuri Amicale Intre Echipe Nationale": "custom-meciuri-amicale"
    }

    def __init__(self):
        self.name_normalizer = NameNormalizer()

    def format_competition_object(self, competition_name, competition_dict):
        try:
             normalized_competition_name = self.name_normalizer.normalize_object_name(competition_name)
             competition_id = self.get_competition_id_from_url(competition_dict['url']) if normalized_competition_name not in self._EXCEPTIONS.keys() else self._EXCEPTIONS[normalized_competition_name]

             return Competition(
                 id=competition_id,
                 country=competition_dict['country'],
                 competition_name=competition_name,
                 url=competition_dict['url'],
                 competition_image_url=competition_dict['competition_image_url']
             )
        except KeyError as e:
            logger.error("Non-existent key: %s", e)
        except Exception as e:
            logger.error("Failed to format competition object: %s", e)

    def format_competition_object_from_full_url(self, competition_url):
        parts = competition_url[:-1].split('/')
        competition_id = parts[-2]
        country = self.name_normalizer.normalize_object_name(parts[4])
        competition_name = self.name_normalizer.normalize_object_name(parts[5])

        return Competition(
            id=competition_id,
            country=country,
            competition_name=competition_name,
            url=competition_url
        )

    def get_competition_id_from_url(self, competition_url):
        parts = competition_url[:-1].split('/')
        hashtag_index = parts.index('#')
        return parts[hashtag_index + 1]

    def get_only_competition_name(self, competition_name):
        return competition_name.split('-')[0].strip()

    def get_frozen_competitions(self, competitions: list[Competition]):
        return [CompetitionFrozen(*astuple(competition)) for competition in competitions]

    def get_unfrozen_competitions(self, frozen_competitions: list[CompetitionFrozen]):
        return [Competition(*astuple(frozen_competition)) for frozen_competition in frozen_competitions]