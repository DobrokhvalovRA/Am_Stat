class Player:
    def __init__(self, participantId, playerName, sportLevel):
        self.participantId = participantId
        self.playerName = playerName
        self.sportLevel = sportLevel

    def __str__(self):
        return self.playerName