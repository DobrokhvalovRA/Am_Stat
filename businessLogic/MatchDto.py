class MatchDto:
    def __init__(self, teamA, teamB, levelDiff):
        self.teamA = teamA
        self.teamB = teamB
        self.levelDiff = levelDiff

    def __str__(self):
        return str(self.teamA) + " VS " + str(self.teamB)