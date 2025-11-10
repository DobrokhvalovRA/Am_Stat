from django.shortcuts import render, redirect
from .models import Tournament

def my_tournaments(request):
    tournaments = Tournament.objects.filter(organizer=request.user)
    return render(request, 'tournaments/my_tournaments.html', {'tournaments': tournaments})

def create_tournament(request):
    if request.method == 'POST':
        # обработка формы, запись в базу
        # отправка данных в телеграм-бот, например через webhook или REST
        pass
    return render(request, 'tournaments/create_tournament.html')

def index(request):
    return render(request, "index.html")