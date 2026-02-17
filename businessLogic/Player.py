class Player:
    def __init__(self, userId, playerName, sportLevel):
        self.userId = userId
        self.playerName = playerName
        self.sportLevel = sportLevel

    def __str__(self):
        return self.playerName