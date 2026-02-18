from django.db import models
from participants.models import Participant
from tournaments.models import Match
    
class TeamComposition(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player1 = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='team_compositions_as_player1')
    player2 = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='team_compositions_as_player2')
    teamNumber = models.PositiveIntegerField()

    def __str__(self):
        nicknames = []
        for player in self.players.all():
            nicknames.append(player.nickname)
        return ", ".join(nicknames)