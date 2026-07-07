from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject

from dataclasses import fields


class DataProcessor:
    def __init__(self):
        pass

    def process_statistics(self, mid, home_team_id, away_team_id, statistics):
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
            category = category.lower()
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