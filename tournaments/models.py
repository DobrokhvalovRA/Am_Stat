from django.db import models
from users.models import User

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

    name = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=150)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    fee = models.DecimalField(max_digits=8, decimal_places=2)
    level = models.CharField(max_length=20)
    players_count = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    sport_type = models.CharField(max_length=100, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_tournaments')

    def __str__(self):
        return f"{self.name} ({self.date})"