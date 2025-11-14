from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_id = models.CharField(max_length=32, unique=True, editable=False)
    nickname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('male', 'Муж'), ('female', 'Жен')])
    phone = models.CharField(max_length=20, blank=True)
    level = models.CharField(max_length=20, blank=True, editable=False)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    rating = models.DecimalField(max_digits=4,decimal_places=2,default=0.00,verbose_name="Рейтинг")

    def get_level_by_rating(self):
        if self.rating <= 12.50:
            return "D"
        elif self.rating <= 25.00:
            return "D+"
        elif self.rating <= 37.50:
            return "C"
        elif self.rating <= 50.00:
            return "C+"
        elif self.rating <= 62.50:
            return "B"
        elif self.rating <= 75.00:
            return "B+"
        elif self.rating <= 87.50:
            return "A"
        else:
            return "A+"

    def save(self, *args, **kwargs):
        self.level = self.get_level_by_rating()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nickname or self.username