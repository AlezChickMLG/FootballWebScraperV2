import logging

from football_repository.football_dataclasses.competition_dataclass import Competition

from football_scraper.NameNormalizer.NameNormalizer import NameNormalizer

logger = logging.getLogger(__name__)

class CompetitionProcessor:
    def __init__(self):
        self.name_normalizer = NameNormalizer()

    def format_competition_object(self, competition_name, competition_dict):
        try:
            parts = competition_dict['url'][:-1].split('/')
            competition_id = parts[-3]
            return Competition(
                id=competition_id,
                country=competition_dict['country'],
                competition_name=competition_name,
                url = competition_dict['url'],
                competition_image_url=competition_dict['competition_image_url']
            )
        except KeyError as e:
            logger.error("Non-existent key: %s", e)
