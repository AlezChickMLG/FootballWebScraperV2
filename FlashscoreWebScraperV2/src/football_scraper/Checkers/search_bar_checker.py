class SearchBarChecker:
    def __init__(self):
        pass

    def is_endpoint_url(self, url):
        return url.startswith('/?r=')

    def is_team(self, url):
        return "echipa" in url

    def is_competition(self, url):
        return "fotbal" in url

    def is_player(self, url):
        return "jucator" in url