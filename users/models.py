from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_id = models.CharField(max_length=32, unique=True)
    nickname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('male', 'Муж'), ('female', 'Жен')])
    phone = models.CharField(max_length=20, blank=True)
    level = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.nickname or self.username