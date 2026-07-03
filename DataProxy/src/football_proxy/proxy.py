from football_scraper.web_scraper import FlashscoreWebScraper
from football_repository.repository import Repository

class Proxy:
    def __init__(self):
        self.flashscoreWebScraper = FlashscoreWebScraper()
        #self.flashscoreWebScraper.process_info({
        #     "team": "Spania"
        # })

        self.repository = Repository()
        #