class NameNormalizer:
    # Romanian diacritics -> ASCII. Defined once at module level instead of
    # rebuilt inside every method that needs to normalize a name.
    DIACRITICS = str.maketrans({"ă": "a", "â": "a", "î": "i", "ș": "s", "ş": "s", "ț": "t", "ţ": "t"})

    def __init__(self):
        pass

    def normalize_single_statistic_name(self, statistic_name):
        if not any([stat in statistic_name for stat in ['xA', 'xG']]):
            return statistic_name.replace('_', ' ').title()
        return statistic_name

    def normalize_object_name(self, team_name):
        return team_name.lower().translate(self.DIACRITICS).replace("-", " ").title()