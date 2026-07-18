import argparse
import logging
from dataclasses import asdict
from types import SimpleNamespace

import flask
from flask import Flask, jsonify

from football_proxy.proxy import Proxy
from football_proxy.data_processors.MatchesSerializer import MatchesSerializer
from football_proxy.data_processors.StatisticsSerializer import StatisticsSerializer

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Flashscore match statistics server")
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Run the browser headless (default: True). Use --no-headless to see it.",
    )
    parser.add_argument(
        "--database-name",
        default="football_database",
        help="SQLite database file (default: football_database)",
    )
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    return parser.parse_args()


#args = parse_arguments()

args = SimpleNamespace(
    log_level="INFO",
    headless=False,
    database_name="football_database",
    debug=True,
    port=8080,
)

logging.basicConfig(
    level=getattr(logging, args.log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = Flask(__name__)

# Build the proxy once. If the browser fails to start (missing Playwright
# binaries, no display, etc.) we want a clear message, not a cryptic stack
# trace on the first request.
try:
    proxy = Proxy(headless=args.headless, database_name=args.database_name)
except Exception as e:
    logger.critical("Failed to start the proxy/browser: %s", e)
    raise

# The serializers share the proxy's repository so they read from the same
# database the proxy writes to — not a second connection to the default file.
match_serializer = MatchesSerializer(repository=proxy.repository)
statistics_serializer = StatisticsSerializer()


def _error(message, status):
    return jsonify({"mesaj_eroare": message}), status


@app.route('/')
def index():
    return flask.render_template("index.html")


@app.route('/get_team/<string:team_name>')
def get_team(team_name):
    try:
        team = proxy.get_team(team_name)
        if not team:
            return _error("echipa inexistenta sau nume echipa incomplet", 404)
        return jsonify(asdict(team)), 200
    except Exception as e:
        logger.exception("get_team failed for %r: %s", team_name, e)
        return _error("eroare interna la gasirea echipei", 500)


@app.route('/get_competition/<string:competition_name>')
def get_competition(competition_name):
    try:
        competition = proxy.get_competition(competition_name)
        if not competition:
            return _error("competitie inexistenta", 404)

        return jsonify(asdict(competition)), 200

    except Exception as e:
        logger.exception("Match search failed for %r: %s", competition_name, e)
        return _error("eroare interna la procesarea meciurilor", 500)


@app.route('/get_matches/<string:team_name>')
def get_matches(team_name):
    return _search_matches(team_name=team_name, fetch_matches=proxy.get_matches)


@app.route('/scan_matches/<string:team_name>')
def scan_matches(team_name):
    return _search_matches(team_name=team_name, fetch_matches=proxy.scan_matches)


def _search_matches(team_name, fetch_matches):
    try:
        team = proxy.get_team(team_name)
        if not team:
            return _error("echipa inexistenta sau nume echipa incomplet", 404)

        matches = fetch_matches(team_name=team.team_name, team_id=team.team_id)
        if not matches:  # None (eroare) sau [] (fara meciuri) sau False
            return _error("nu s-au gasit meciuri pentru aceasta echipa", 404)

        serialized = match_serializer.serialize_matches(matches)
        sorted_matches = match_serializer.sort_serialized_matches_by_start_time(serialized)
        return jsonify(sorted_matches), 200
    except Exception as e:
        logger.exception("Match search failed for %r: %s", team_name, e)
        return _error("eroare interna la procesarea meciurilor", 500)

@app.route('/get_statistics/<string:mid>')
def get_statistics(mid):
    try:
        match = proxy.get_match_by_mid(mid)
        if match is None:
            return _error("meci inexistent", 404)

        statistics = proxy.get_match_statistics(match)
        if not statistics:
            return _error("statistici indisponibile pentru acest meci", 404)

        serialized = statistics_serializer.serialize_statistics(statistics)
        if serialized is None:
            return _error("statistici indisponibile pentru acest meci", 404)

        normalized = statistics_serializer.normalize_serialized_names(serialized)
        return jsonify(normalized), 200
    except Exception as e:
        logger.exception("get_statistics failed for %r: %s", mid, e)
        return _error("eroare interna la obtinerea statisticilor", 500)


if __name__ == '__main__':
    app.run(
        debug=args.debug,
        port=args.port,
        threaded=False,
        use_reloader=False,
    )