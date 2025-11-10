from django.db import models
from users.models import User
from tournaments.models import Tournament

class Participant(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='participant_links'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.nickname} в {self.tournament.name}"