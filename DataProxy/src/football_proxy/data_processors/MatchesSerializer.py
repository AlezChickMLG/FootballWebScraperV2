import logging
from datetime import datetime

from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.repository import Repository

logger = logging.getLogger(__name__)


class MatchesSerializer:
    def __init__(self, repository: Repository = None):
        # Share the caller's repository so we read from the same database the
        # proxy writes to. Falling back to a new Repository() would open the
        # default file and silently return None for every team.
        self.repository = repository if repository is not None else Repository()

    def serialize_matches(self, matches: list[Match]):
        """Turn a list of Match objects into a list of serialized dicts.
        Matches whose teams can't be resolved are skipped, not fatal."""
        serialized_matches = []

        for match in matches:
            try:
                home_team = self.repository.get_team_by_id(match.home_team)
                away_team = self.repository.get_team_by_id(match.away_team)

                if home_team is None or away_team is None:
                    logger.warning(
                        "Skipping match %s: team not found (home=%s, away=%s)",
                        match.mid, match.home_team, match.away_team,
                    )
                    continue

                serialized_matches.append(self._serialize_match(match, home_team, away_team))
            except Exception as e:
                logger.error("Failed to serialize match %s: %s", getattr(match, "mid", "?"), e)

        return serialized_matches

    @staticmethod
    def _serialize_match(match: Match, home_team: Team, away_team: Team):
        return {
            'mid': match.mid,
            'home_team': home_team.team_name,
            'home_team_id': home_team.team_id,
            'home_flag': home_team.image_url,
            'away_team': away_team.team_name,
            'away_team_id': away_team.team_id,
            'away_flag': away_team.image_url,
            'start_time': match.start_time,
            'match_score': match.match_score,
        }

    @staticmethod
    def sort_serialized_matches_by_start_time(matches: list[dict]):
        """Sort serialized matches by start_time, most recent first. Entries
        with an unparseable date go to the end instead of crashing the sort."""
        def sort_key(serialized_match):
            raw = serialized_match.get("start_time")
            try:
                return datetime.strptime(raw, "%d.%m.%Y")
            except (ValueError, TypeError):
                logger.warning("Unsortable start_time %r for match %s",
                               raw, serialized_match.get("mid"))
                return datetime.min

        return sorted(matches, key=sort_key, reverse=True)