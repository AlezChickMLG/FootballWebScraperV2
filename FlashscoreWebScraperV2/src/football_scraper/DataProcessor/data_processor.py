import logging
from datetime import datetime

from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.competition_dataclass import Competition
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject

from football_scraper.NameNormalizer.NameNormalizer import NameNormalizer

logger = logging.getLogger(__name__)

# Category label (lowercaxsed, de-diacriticized) -> statistics dataclass.
CATEGORY_TO_CLASS = {
    "top statistici": TopStatisticsObject,
    "suturi": SuturiObject,
    "atac": AtacObject,
    "pase": PaseObject,
    "aparare": AparareObject,
    "portari": PortarObject,
}

# Characters stripped when splitting a "procent% (reusite/totale)" value.
_VALUE_SEPARATORS = str.maketrans({"%": " ", "(": " ", "/": " ", ")": " "})

_FLASHSCORE_BASE = "https://www.flashscore.ro"


class DataProcessor:
    def __init__(self):
        self.name_normalizer = NameNormalizer()

    # ------------------------------------------------------------------ #
    #  Team formatting                                                   #
    # ------------------------------------------------------------------ #
    def _build_team_url(self, team_name, team_id):
        slug = team_name.lower().replace(" ", "-")
        return f"{_FLASHSCORE_BASE}/echipa/{slug}/{team_id}"

    def _build_competition_url(self, competition_name, country):
        competition_name_slug = competition_name.lower().replace(" ", "-")
        country_slug = country.lower().replace(" ", "-")
        return f"{_FLASHSCORE_BASE}/fotbal/{country_slug}/{competition_name_slug}"

    def get_id_from_endpoint_url(self, team_url):
        return team_url.split(':')[-1]

    def format_team_object_from_url(self, team_name, team_url, team_image_url=""):
        team_id = team_url.split(":")[-1]
        return Team(
            team_id=team_id,
            team_name=self.name_normalizer.normalize_object_name(team_name),
            url=self._build_team_url(team_name, team_id),
            image_url=team_image_url,
        )

    def format_team_object_from_id(self, team_name, team_id, team_image_url=""):
        return Team(
            team_id=team_id,
            team_name=self.name_normalizer.normalize_object_name(team_name),
            url=self._build_team_url(team_name, team_id),
            image_url=team_image_url,
        )

    # ------------------------------------------------------------------ #
    #  Competition formatting                                            #
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    #  Match formatting                                                  #
    # ------------------------------------------------------------------ #
    def filter_matches(self, matches, home_team, away_team=None, start_time=None,
                       start_date=None, finish_date=None, competition=None):
        return matches

    def format_matches(self, matches):
        formatted_matches = []
        for match in matches:
            formatted = self._format_single_match(match)
            if formatted is not None:
                formatted_matches.append(formatted)
        return formatted_matches

    def _format_single_match(self, match):
        """Parse one raw match dict into {home_team, away_team, match} or None."""
        try:
            match['home_team'] = self.name_normalizer.normalize_object_name(match['home_team'])
            match['away_team'] = self.name_normalizer.normalize_object_name(match['away_team'])

            first_raw, second_raw, mid_raw = match["match_url"].split("/")[-3:]

            first_name, first_id = first_raw.rsplit("-", maxsplit=1)
            first_team = self.format_team_object_from_id(
                team_name=first_name, team_id=first_id,
                team_image_url=match["home_team_image_url"],
            )

            second_name, second_id = second_raw.rsplit("-", maxsplit=1)
            second_team = self.format_team_object_from_id(
                team_name=second_name, team_id=second_id,
                team_image_url=match["away_team_image_url"],
            )

            # The URL order isn't guaranteed to be home-then-away; match the
            # scraped home_team name to decide which parsed team is which.
            if first_team.team_name == match["home_team"]:
                home_team, away_team = first_team, second_team
            else:
                home_team, away_team = second_team, first_team

            home_team.image_url = match["home_team_image_url"]
            away_team.image_url = match["away_team_image_url"]

            mid = mid_raw.split("=")[-1]
            formatted_match = Match(
                mid=mid,
                home_team=home_team.team_id,
                away_team=away_team.team_id,
                start_time=match["start_time"],
                match_url=match["match_url"],
                match_score=match["score"],
                is_played=1,
            )

            return {"home_team": home_team, "away_team": away_team, "match": formatted_match}
        except Exception as e:
            logger.error("Failed to format match %s: %s", match.get("match_url", match), e)
            return None

    def process_start_time(self, start_time):
        """Return (datetime, 'dd.mm.YYYY' string). Handles both a full date and
        the 'dd.mm. HH:MM' form the scraper sometimes yields for recent games."""
        start_time = start_time.split("\n")[0]
        try:
            parsed = datetime.strptime(start_time, "%d.%m.%Y")
            return parsed, start_time
        except ValueError:
            pass

        try:
            parsed = datetime.strptime(start_time, "%d.%m. %H:%M")
            parsed = parsed.replace(year=datetime.now().year)
            return parsed, parsed.strftime("%d.%m.%Y")
        except ValueError:
            logger.warning("Unknown start_time format: %r", start_time)
            return None, None

    # ------------------------------------------------------------------ #
    #  Statistics processing                                             #
    # ------------------------------------------------------------------ #
    def process_statistics(self, mid, home_team_id, away_team_id, statistics):
        """Turn the scraped {category: {stat_name: {home, away}}} structure into
        two dicts of dataclass objects, one per team, keyed by category."""
        try:
            home_team_statistics = {}
            away_team_statistics = {}

            for raw_category, category_values in statistics.items():
                category = self._normalize_category(raw_category)
                if category not in CATEGORY_TO_CLASS:
                    logger.warning("Unknown statistics category: %r", raw_category)
                    continue

                home_values, away_values = self._extract_category_values(category, category_values)

                stat_class = CATEGORY_TO_CLASS[category]
                home_team_statistics[category] = stat_class(
                    mid=mid, team_id=home_team_id, **home_values
                )
                away_team_statistics[category] = stat_class(
                    mid=mid, team_id=away_team_id, **away_values
                )

            return home_team_statistics, away_team_statistics
        except Exception as e:
            logger.error("Failed to process statistics for match %s: %s", mid, e)
            return False

    def _normalize_category(self, category):
        return category.lower().translate(NameNormalizer.DIACRITICS)

    def _extract_category_values(self, category, category_values):
        """Build {column: value} dicts for home and away from one category's
        raw {stat_name: {home, away}} mapping."""
        home_values = {}
        away_values = {}

        for raw_name, pair in category_values.items():
            try:
                name = self._normalize_stat_name(raw_name, category)
                self._assign_stat(name, pair, home_values, away_values)
            except Exception as e:
                logger.error("Failed to process stat %r: %s", raw_name, e)

        return home_values, away_values

    def _normalize_stat_name(self, name, category):
        """Map a raw Romanian stat label to its dataclass column name."""
        # Expected-goals family keeps canonical short names. For goalkeepers,
        # xGOT is stored as xGOT_impotriva (the value conceded).
        if "xGOT" in name:
            return "xGOT_impotriva" if category == "portari" else "xGOT"
        if "xG" in name:
            return "xG"
        if "xA" in name:
            return "xA"

        normalized = name.replace(" ", "_").lower().translate(NameNormalizer.DIACRITICS)

        if normalized.startswith("erori"):
            if normalized.endswith("sut"):
                return "erori_sut"
            if normalized.endswith("gol"):
                return "erori_gol"

        return normalized

    def _assign_stat(self, name, pair, home_values, away_values):
        """Write one stat into the home/away dicts, splitting percent-and-count
        values like '82% (451/550)' into _procentaj/_reusite/_totale columns."""
        home_raw = pair["home"]
        away_raw = pair["away"]

        both_strings = isinstance(home_raw, str) and isinstance(away_raw, str)
        has_percent = both_strings and ("%" in home_raw or "%" in away_raw)

        if not has_percent:
            home_values[name] = home_raw
            away_values[name] = away_raw
            return

        has_slash = "/" in home_raw or "/" in away_raw
        if has_slash:
            self._assign_percent_triplet(name, home_raw, home_values)
            self._assign_percent_triplet(name, away_raw, away_values)
        else:
            home_values[name] = home_raw.replace("%", "")
            away_values[name] = away_raw.replace("%", "")

    def _assign_percent_triplet(self, name, raw_value, target):
        """'82% (451/550)' -> {name_procentaj: 82, name_reusite: 451, name_totale: 550}."""
        procentaj, reusite, totale = raw_value.translate(_VALUE_SEPARATORS).split()
        target[f"{name}_procentaj"] = procentaj
        target[f"{name}_reusite"] = reusite
        target[f"{name}_totale"] = totale