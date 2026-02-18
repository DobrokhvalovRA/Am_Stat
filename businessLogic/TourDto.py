class TourDto:
    def __init__(self, number):
        self.matches = []
        self.number = number

    def addMatch(self, match):
        self.matches.append(match)