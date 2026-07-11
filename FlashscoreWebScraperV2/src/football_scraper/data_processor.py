from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.matches_dataclass import Match
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.teams_dataclass import Team
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject

from dataclasses import fields
from datetime import datetime

class DataProcessor:
    def __init__(self):
        pass

    def filter_matches(self, matches, home_team, away_team=None, start_time=None, start_date=None, finish_date=None, competition=None):
        return matches

    def format_matches(self, matches):
        formatted_matches = []
        for match in matches:
            try:
                first_team, second_team, mid = match['match_url'].split("/")[-3:]

                first_team_name, first_team_id = first_team.rsplit("-", maxsplit=1)
                formatted_first_team = self.format_team_object_from_id(team_name=first_team_name, team_id=first_team_id, team_image_url=match['home_team_image_url'])

                second_team_name, second_team_id = second_team.rsplit("-", maxsplit=1)
                formatted_second_team = self.format_team_object_from_id(team_name=second_team_name, team_id=second_team_id, team_image_url=match['away_team_image_url'])

                if formatted_first_team.team_name == match['home_team']:
                    formatted_home_team = formatted_first_team
                    formatted_away_team = formatted_second_team

                else:
                    formatted_home_team = formatted_second_team
                    formatted_away_team = formatted_first_team

                home_team_id = formatted_home_team.team_id
                formatted_home_team.image_url = match['home_team_image_url']

                away_team_id = formatted_away_team.team_id
                formatted_away_team.image_url = match['away_team_image_url']

                mid = mid.split("=")[-1]
                formatted_match = Match(
                    mid=mid,
                    home_team=home_team_id,
                    away_team=away_team_id,
                    start_time=match['start_time'],
                    match_url=match['match_url'],
                    match_score="",
                    is_played=1
                )

                formatted_matches.append({
                    "home_team": formatted_home_team,
                    "away_team": formatted_away_team,
                    "match": formatted_match
                })
            except Exception as e:
                print(f"Eroare la formatarea: {match}")
        return formatted_matches

    def process_start_time(self, start_time):
        try:
            start_time = start_time.split("\n")[0]
            formatted_start_time = datetime.strptime(start_time, "%d.%m.%Y")
            return formatted_start_time, start_time
        except ValueError:
            try:
                hour_start_time = datetime.strptime(start_time, "%d.%m. %H:%M")
                hour_start_time = hour_start_time.replace(year=datetime.now().year)
                return hour_start_time, hour_start_time.strftime("%d.%m.%Y")
            except ValueError:
                print("Format necunoscut")

    def process_statistics(self, mid, home_team_id, away_team_id, statistics):
        try:

            self.classses_map = {
                "top statistici": TopStatisticsObject,
                "suturi": SuturiObject,
                "atac": AtacObject,
                "pase": PaseObject,
                "aparare": AparareObject,
                "portari": PortarObject
            }

            home_team_statistics = {}
            away_team_statistics = {}

            for category, statistics_values in statistics.items():
                category = category.lower().translate(str.maketrans({
                                "ă": "a",
                                "â": "a",
                                "î": "i",
                                "ș": "s",
                                "ț": "t"
                            }))
                home_team_values = {}
                away_team_values = {}
                for statistics_name, statistics_pair_values in statistics_values.items():
                    #prelucrare nume
                    try:
                        if any(specific_name in statistics_name for specific_name in ["xG", "xA"]):
                            if "xGOT" in statistics_name:
                                if category != "portari":
                                    statistics_name = "xGOT"
                                else:
                                    statistics_name = "xGOT_impotriva"
                            elif "xG" in statistics_name:
                                statistics_name = "xG"
                            else:
                                statistics_name = "xA"

                        else:
                            statistics_name = ((statistics_name.replace(" ", "_")
                                                .lower())
                            .translate(str.maketrans({
                                "ă": "a",
                                "â": "a",
                                "î": "i",
                                "ș": "s",
                                "ț": "t"
                            })))

                        if statistics_name.startswith("erori"):
                            if statistics_name.endswith("sut"):
                                statistics_name = "erori_sut"
                            elif statistics_name.endswith("gol"):
                                statistics_name = "erori_gol"

                        if isinstance(statistics_pair_values['home'], str) and isinstance(statistics_pair_values['away'],
                                                                                          str):
                            if "%" in statistics_pair_values['home'] or "%" in statistics_pair_values['away']:
                                if "/" in statistics_pair_values['home'] or "/" in statistics_pair_values['away']:
                                    get_values_function = lambda x: x.translate(str.maketrans({
                                        "%": " ",
                                        "(": " ",
                                        "/": " ",
                                        ")": " "
                                    })).split()

                                    procentaj_home, reusite_home, totale_home = get_values_function(
                                        statistics_pair_values['home'])
                                    home_team_values[f"{statistics_name}_procentaj"] = procentaj_home
                                    home_team_values[f"{statistics_name}_reusite"] = reusite_home
                                    home_team_values[f"{statistics_name}_totale"] = totale_home

                                    procentaj_away, reusite_away, totale_away = get_values_function(
                                        statistics_pair_values['away'])

                                    away_team_values[f"{statistics_name}_procentaj"] = procentaj_away
                                    away_team_values[f"{statistics_name}_reusite"] = reusite_away
                                    away_team_values[f"{statistics_name}_totale"] = totale_away

                                else:
                                    statistics_pair_values['home'] = statistics_pair_values['home'].replace("%", "")
                                    home_team_values[statistics_name] = statistics_pair_values['home']

                                    statistics_pair_values['away'] = statistics_pair_values['away'].replace("%", "")
                                    away_team_values[statistics_name] = statistics_pair_values['away']

                        else:
                            home_team_values[statistics_name] = statistics_pair_values['home']
                            away_team_values[statistics_name] = statistics_pair_values['away']

                    except Exception as e:
                        print(f"Eroare la procesarea statisticilor: {e}")

                home_team_object = self.classses_map[category](mid=mid, team_id=home_team_id, **home_team_values)
                home_team_statistics[category] = home_team_object

                away_team_object = self.classses_map[category](mid=mid, team_id=away_team_id, **away_team_values)
                away_team_statistics[category] = away_team_object

                return home_team_statistics, away_team_statistics

        except Exception as e:
            print(f"Eroare la formatarea statisticilor: {e}")
            return False

    def format_team_name(self, team_name):
        return team_name.lower().translate(str.maketrans({
                                "ă": "a",
                                "â": "a",
                                "î": "i",
                                "ș": "s",
                                "ț": "t"
                            })).replace("-", " ").title()

    def format_team_object_from_url(self, team_name, team_url, team_image_url=''):
        return Team(
            team_id=team_url.split(':')[-1],
            team_name=self.format_team_name(team_name),
            url=f"https://www.flashscore.ro/echipa/{team_name.lower().replace(' ', '-')}/{team_url.split(':')[-1]}",
            image_url=team_image_url
        )

    def format_team_object_from_id(self, team_name, team_id, team_image_url=''):
        return Team(
            team_id=team_id,
            team_name=self.format_team_name(team_name),
            url=f"https://www.flashscore.ro/echipa/{team_name.lower().replace(' ', '-')}/{team_id}",
            image_url=team_image_url
        )