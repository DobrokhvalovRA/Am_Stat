from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from . import models
from participants.models import Participant
from models.TeamComposition import TeamComposition
from models.DataAccessManager import SaveTour
from businessLogic import Player
from businessLogic import Generator

class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "organizer")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:tournament_id>/start/', self.admin_site.admin_view(self.start_tournament_view), name='tournament-start'),
            path('<int:tournament_id>/custom_change/', self.admin_site.admin_view(self.custom_change_view), name='tournament-custom-change'),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        tournament = get_object_or_404(models.Tournament, pk=object_id)
        return render(request, 'admin/tournaments/custom_change_buttons.html', {
            'tournament': tournament,
        })

    def custom_change_view(self, request, tournament_id):
        # Перенаправление на стандартную админ-форму
        return super().change_view(request, str(tournament_id))

    def start_tournament_view(request, tournament_id):
        activeStatus = 'active'
        tournament = get_object_or_404(models.Tournament, pk=tournament_id)
        if tournament.status == activeStatus:
            raise BaseException("Турнир уще начат, невозможно начать его заново.")
        participants = Participant.objects.filter(tournament=tournament)
        players = []
        for participant in participants:
            sportLevels = participant.user.sportlevel_set.filter(sport_type__contains="beach_volleyball")
            if len(sportLevels) != 1:
                raise BaseException("У пользователя " + str(participant.user) + " не указан уровень игры в пляжный воллейбол")
            players.append(Player.Player(participant.id, str(participant.user), sportLevels[0].rating))
        tours = Generator.Generator.GenerateMatchesAmericano(players, 0)
        for tour in tours:
            SaveTour(tour, tournament)
        tournament.status = activeStatus
        tournament.save()
        return render(request, 'tournaments/tournament_start.html', {
            'tournament': tournament,
            'participants': participants,
            'tours': tours
        })

admin.site.register(models.Tournament, TournamentAdmin)
admin.site.register(models.Tour)
admin.site.register(TeamComposition)
admin.site.register(models.Match)

"""from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tournament
from participants.models import Participant

class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "organizer")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:tournament_id>/start/', self.admin_site.admin_view(self.start_tournament_view),
                 name='tournament-start'),
            path('<int:tournament_id>/custom_change/', self.admin_site.admin_view(self.custom_change_view),
                 name='tournament-custom-change'),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Вместо стандартной формы показываем кастомную страницу с кнопками
        extra_context = extra_context or {}
        tournament = get_object_or_404(Tournament, pk=object_id)
        extra_context['custom_admin_buttons'] = {
            'edit_url': f'{object_id}/custom_change/',
            'start_url': f'{object_id}/start/',
        }
        return render(request, 'admin/tournaments/custom_change_buttons.html', {
            'tournament': tournament,
            'custom_admin_buttons': extra_context['custom_admin_buttons'],
        })

    def custom_change_view(self, request, tournament_id):
        # Стандартная форма редактирования
        return super().change_view(request, str(tournament_id))

    def start_tournament_view(self, request, tournament_id):
        tournament = get_object_or_404(Tournament, pk=tournament_id)
        participants = Participant.objects.filter(tournament=tournament)
        return render(request, 'admin/tournaments/tournament_start.html', {
            'tournament': tournament,
            'participants': participants,
        })

admin.site.register(Tournament, TournamentAdmin)"""