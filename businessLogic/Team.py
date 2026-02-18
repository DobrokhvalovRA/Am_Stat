class Team:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def __str__(self):
        return str(self.player1) + " + " + str(self.player2)