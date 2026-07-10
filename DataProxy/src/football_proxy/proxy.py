from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject
from football_repository.frozen_football_dataclasses.frozen_matches_dataclass import MatchFrozen
from football_repository.frozen_football_dataclasses.frozen_teams_dataclass import TeamFrozen
from football_scraper.web_scraper import FlashscoreWebScraper
from football_repository.repository import Repository
from datetime import datetime
from football_repository.football_dataclasses.matches_dataclass import Match
from football_scraper.data_processor import DataProcessor

class Proxy:
    def __init__(self, headless=True):
        self.flashscore_web_scraper = FlashscoreWebScraper(headless)
        self.data_processor = DataProcessor()
        self.repository = Repository()

    def get_team(self, team_name):
        formatted_team = self.repository.get_team_by_name(team_name)

        if not formatted_team:
            team_url = self.flashscore_web_scraper.get_team_url(team_name)

            #format team
            formatted_team = self.data_processor.format_team_object_from_url(team_name=team_name, team_url=team_url)

            #actualizam baza de date
            self.repository.insert_team(formatted_team)

        return formatted_team

    def get_matches(self, home_team_name, home_team_id,  away_team_name=None, away_team_id=None, start_time=None, start_date=None, finish_date=None, competition=None):
        all_matches = self.repository.get_match_by_details(home_team=home_team_id, away_team=away_team_id, start_time=start_time)

        if all_matches is None or len(all_matches) == 0:
            try:
                all_matches = self.flashscore_web_scraper.get_all_matches(team_name=home_team_name, team_id=home_team_id)
                formatted_matches_with_teams = self.data_processor.format_matches(all_matches)
                formatted_matches = []

                for match in formatted_matches_with_teams:

                    match['home_team'].team_name = match['home_team'].team_name.title().replace("-", " ")
                    self.repository.insert_team(match['home_team'])

                    match['away_team'].team_name = match['away_team'].team_name.title().replace("-", " ")
                    self.repository.insert_team(match['away_team'])

                    self.repository.insert_match(match['match'])
                    formatted_matches.append(match['match'])

                return formatted_matches

                #all_matches = self.data_processor.filter_matches(matches=formatted_matches, home_team=home_team, away_team=away_team, start_time=start_time,
                #                                                      start_date=start_date, finish_date=finish_date, competition=competition)
            except Exception as e:
                print(f"Eroare: {e}")
                return False

        else:
            return all_matches

    def get_statistics(self, matches: list[Match]):
        try:
            statistics_dict = {}

            selection_list = [
                self.repository.get_top_statistics_by_id,
                self.repository.get_pase_by_id,
                self.repository.get_atac_by_id,
                self.repository.get_suturi_by_id,
                self.repository.get_aparare_by_id,
                self.repository.get_portari_by_id
            ]

            for match in matches:
                statistics_dict.setdefault(match.mid, {})
                for team in [match.home_team, match.away_team]:
                    #verificam daca avem toate statisticile
                    #daca toate sunt inexistente, scanam pentru statistici
                    if all([selection_function(mid=match.mid, team_id=team) is None for selection_function in selection_list]):

                        # obtinem statisticile
                        raw_statistics = self.flashscore_web_scraper.get_statistics(match_url=match.match_url)

                        #obtinem imaginile echipelor
                        home_team_image_url, away_team_image_url = self.flashscore_web_scraper.get_team_flags_from_statistics()

                        # formatam statisticile
                        formatted_statistics = self.data_processor.process_statistics(mid=match.mid,
                                                                                      home_team_id=match.home_team,
                                                                                      away_team_id=match.away_team,
                                                                                      statistics=raw_statistics)

                        # inseram datele gasite
                        insertion_dict = {
                            TopStatisticsObject: self.repository.insert_top_statistic,
                            SuturiObject: self.repository.insert_suturi,
                            PaseObject: self.repository.insert_pase,
                            AtacObject: self.repository.insert_atac,
                            AparareObject: self.repository.insert_aparare,
                            PortarObject: self.repository.insert_portar
                        }

                        for each_team_statistics in formatted_statistics:
                            for statistic_name, statistic_class in each_team_statistics.items():
                                insertion_dict[type(statistic_class)](statistic_class)

                        statistics_dict[match.mid][match.home_team] = formatted_statistics[0]
                        statistics_dict[match.mid][match.away_team] = formatted_statistics[1]
                        break

                    else:
                        formatted_statistics = [selection_function(mid=match.mid, team_id=team) for selection_function in selection_list]

                    statistics_dict[match.mid][team] = formatted_statistics

            return statistics_dict
        except Exception as e:
            print(f"Eroare la prelucrarea statisticilor: {e}")
            return None