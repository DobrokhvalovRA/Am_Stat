from django.contrib import admin
from .models import User, SportLevel

"""class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "nickname", "rating", "level")
    readonly_fields = ("telegram_id", "level")  # запрещаем редактировать
admin.site.register(User, UserAdmin)"""

class SportLevelInline(admin.TabularInline):
    model = SportLevel
    extra = 0

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "nickname", "gender", "phone", "telegram_id")
    readonly_fields = ("telegram_id",)
    inlines = [SportLevelInline]

    def get_levels(self, obj):
        levels = [f"{sl.sport_type}: {sl.level} ({sl.rating})" for sl in obj.sportlevel_set.all()]
        return "; ".join(levels) if levels else "Нет данных"

    get_levels.short_description = "Уровни игрока"

admin.site.register(User, UserAdmin)