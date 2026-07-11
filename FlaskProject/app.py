from dataclasses import asdict

import flask
from flask import Flask, jsonify
from football_proxy.proxy import Proxy
from datetime import datetime

app = Flask(__name__)
proxy = Proxy(headless=False)

@app.route('/')
def hello_world():  # put application's code here
    return flask.render_template("index.html")

@app.route(f'/get_matches/<string:team_name>')
def get_matches(team_name):
    team = proxy.get_team(team_name)

    if team is None or team is False:
        return jsonify({
            'mesaj_eroare': 'echipa inexistenta sau nume echipa incomplet'
        }), 404

    else:
        matches = proxy.get_matches(team_name=team.team_name, team_id=team.team_id)
        if matches is False:
            return jsonify({
                'mesaj_eroare': 'eroare la procesarea echipelor'
            }), 404

        formatted_matches = []

        for match in matches:
            home_team = proxy.get_team_by_id(team_id=match.home_team)
            away_team = proxy.get_team_by_id(team_id=match.away_team)

            formatted_matches.append({
                'home_team': home_team.team_name,
                'home_flag': home_team.image_url,
                'away_team': away_team.team_name,
                'away_flag': away_team.image_url,
                'start_time': match.start_time
            })

    formatted_matches.sort(key=lambda formatted_match: datetime.strptime(formatted_match["start_time"], "%d.%m.%Y"), reverse=True)
    return jsonify(formatted_matches), 200

if __name__ == '__main__':
    app.run(debug=True)
