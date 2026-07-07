from functools import reduce

from football_repository.football_dataclasses.aparare_dataclass import AparareObject
from football_repository.football_dataclasses.atac_dataclass import AtacObject
from football_repository.football_dataclasses.pase_dataclass import PaseObject
from football_repository.football_dataclasses.portar_dataclass import PortarObject
from football_repository.football_dataclasses.suturi_dataclass import SuturiObject
from football_repository.football_dataclasses.topStatistics_dataclass import TopStatisticsObject
from football_scraper.web_scraper import FlashscoreWebScraper
from football_repository.repository import Repository
from datetime import datetime
from football_repository.football_dataclasses.matches_dataclass import Match
from football_scraper.data_processor import DataProcessor

class Proxy:
    def __init__(self):
        self.flashscore_web_scraper = FlashscoreWebScraper()
        self.data_processor = DataProcessor()
        self.repository = Repository()

    def get_team(self, team_name):
        team = self.repository.get_team_by_name(team_name)

        if not team:
            team = self.flashscore_web_scraper.get_team_url(team_name)

            #actualizam baza de date
            self.repository.insert_team(team)

        return team

    def get_matches(self, home_team, away_team=None, start_time=None, start_date=None, finish_date=None, competition=None):
        all_matches = self.repository.get_match_by_details(home_team=home_team, away_team=away_team, start_time=start_time)

        if not all_matches:
            pass

        # else:
        #     matches_not_played = self.repository.get_matches_by_is_played(is_played=False)
        #     #exista meciuri jucate care nu au fost scanate
        #     if matches_not_played:
        #         print("Trebuie sa rulez din nou flashscore web scraper")
        #         #gasim cel mai vechi meci nejucat
        #         oldest_match_not_played = min(
        #             matches_not_played,
        #             key=lambda match: datetime.strptime(match.start_time, "%d.%m.%Y")
        #         )
        #
        #         #in viitor trebuie pus un time limit
        #         #scanam iar meciurile, dar doar cele care nu exista deja
        #         time_limit = datetime.strptime(oldest_match_not_played.start_time, "%d.%m.%Y")
        #
        #     #toate meciurile sunt scanate deja
        #     else:
        #         pass

        return all_matches

    def scan_matches_for_statistics(self, matches: list[Match]):
        for match in matches:
            selection_list = [
                self.repository.get_top_statistics_by_id,
                self.repository.get_pase_by_id,
                self.repository.get_atac_by_id,
                self.repository.get_suturi_by_id,
                self.repository.get_aparare_by_id,
                self.repository.get_portari_by_id
            ]

            for team in [match.home_team, match.away_team]:
                #verificam daca avem toate statisticile
                #daca toate sunt inexistente, scanam pentru statistici
                if all([selection_function(mid=match.mid, team_id=team) is None for selection_function in selection_list]):

                    # obtinem statisticile
                    raw_statistics = self.flashscore_web_scraper.get_statistics(match_url=match.match_url)

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

                    break

