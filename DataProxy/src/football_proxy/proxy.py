from football_scraper.web_scraper import FlashscoreWebScraper
from football_repository.repository import Repository
from datetime import datetime
from football_repository.football_dataclasses.matches_dataclass import Match

class Proxy:
    def __init__(self):
        self.flashscoreWebScraper = FlashscoreWebScraper()
        self.repository = Repository()

    def get_team(self, team_name):
        team = self.repository.get_team_by_name(team_name)

        if not team:
            team = self.flashscoreWebScraper.get_team_url(team_name)

            #actualizam baza de date
            self.repository.insert_team(team)

        return team

    def get_matches(self, home_team, away_team=None, start_time=None, start_date=None, finish_date=None, competition=None):
        all_matches = self.repository.get_match_by_details(home_team=home_team, away_team=away_team, start_time=start_time)

        if not all_matches:
            pass

        else:
            earliest_match = max(all_matches, key=lambda match: datetime.strptime(match.start_time, "%d.%m.%y"))
            if earliest_match > datetime.now():
                print("Trebuie sa rulez din nou flashscore web scraper")

        return all_matches

