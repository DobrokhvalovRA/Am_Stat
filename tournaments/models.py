from django.db import models
from users.models import User
from multiselectfield import MultiSelectField

class Tournament(models.Model):
    FORMAT_CHOICES = [
        ('solo', 'Одиночный'),
        ('pair', 'Парный')
    ]
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('cancelled', 'Отменён'),
        ('finished', 'Завершён'),
    ]
    LEVEL_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D+', 'D+'),
        ('D', 'D'),
    ]

    SPORT_TYPE_CHOICES = [
        ('beach_volleyball', 'Пляжный волейбол'),
        ('beach_tennis', 'Пляжный теннис'),
    ]

    name = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=150)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    fee = models.DecimalField(max_digits=8, decimal_places=2)
    level = MultiSelectField(choices=LEVEL_CHOICES, default=[], blank=True, verbose_name='Допустимые уровни')
    players_count = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    sport_type = models.CharField(max_length=32, choices=SPORT_TYPE_CHOICES, default='beach_volleyball', verbose_name='Вид спорта')
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_tournaments')

    participants = models.ManyToManyField(
        User,
        through='participants.Participant',
        related_name='tournaments_participated'
    )
    tg_chat_id = models.CharField(max_length=32, blank=True, null=True)
    tg_message_id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

class Round(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return f"Раунд № {self.number}"
    
class GameTeam(models.Model):
    players = models.ManyToManyField(User)

    def __str__(self):
        nicknames = []
        for player in self.players.all():
            nicknames.append(player.nickname)
        return ", ".join(nicknames)
    
class Game(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    teams = models.ManyToManyField(GameTeam)

    def __str__(self):
        allTeams = self.teams.all();
        return str(allTeams[0]) + " VS " + str(allTeams[1])
