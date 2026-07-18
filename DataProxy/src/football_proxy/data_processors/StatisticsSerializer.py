import logging
from dataclasses import fields

from football_scraper.NameNormalizer.NameNormalizer import NameNormalizer

logger = logging.getLogger(__name__)


class StatisticsSerializer:
    _SKIP = {"mid", "team_id"}
    _EMPTY_STR = ''
    _EMPTY_NUM = -1

    def __init__(self):
        self.name_normalizer = NameNormalizer()

    def serialize_statistics(self, statistics):
        """
        statistics: {team_id: {category: dataclass}}  — expected two teams
        return:     {category: {stat_name: {home, away}}}  or None on bad input
        """
        if not statistics:
            logger.warning("serialize_statistics got empty input")
            return None

        teams = list(statistics.values())
        if len(teams) != 2:
            # Scraping may have produced one team or none — can't build a
            # home/away comparison, so bail cleanly instead of unpacking-crash.
            logger.warning("Expected 2 teams in statistics, got %d", len(teams))
            return None

        home_statistics, away_statistics = teams

        try:
            return {
                category: self._serialize_category(home_object, away_statistics.get(category))
                for category, home_object in home_statistics.items()
            }
        except Exception as e:
            logger.error("Failed to serialize statistics: %s", e)
            return None

    def _is_set(self, value):
        """A field counts as 'set' if it's not the dataclass empty sentinel."""
        if value is None:
            return False
        if isinstance(value, str):
            return value != self._EMPTY_STR
        if isinstance(value, (int, float)):
            return value != self._EMPTY_NUM
        return True

    def _serialize_category(self, home_object, away_object):
        if home_object is None:
            return {}

        result = {}
        for field in fields(home_object):
            if field.name in self._SKIP:
                continue

            home_value = getattr(home_object, field.name)
            away_value = getattr(away_object, field.name) if away_object is not None else None

            # Keep a stat only if both sides have a real value; otherwise the
            # UI would show a lonely number against a blank.
            if self._is_set(home_value) and self._is_set(away_value):
                result[field.name] = {"home": home_value, "away": away_value}

        return result

    def normalize_serialized_names(self, statistics):
        """Normalize all stat names into a readable form."""
        if not statistics:
            return {}

        normalized = {}
        for category_name, stat_dict in statistics.items():
            normalized[category_name] = {
                self.name_normalizer.normalize_single_statistic_name(stat_name): values
                for stat_name, values in stat_dict.items()
            }
        return normalized