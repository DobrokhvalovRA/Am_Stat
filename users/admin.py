from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "nickname", "rating", "level")
    readonly_fields = ("telegram_id", "level")  # запрещаем редактировать



admin.site.register(User, UserAdmin)