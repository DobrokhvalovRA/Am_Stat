from django.shortcuts import render, redirect, get_object_or_404
from tournaments.models import Tournament, User
from participants.models import Participant
from .telegram_notify import send_tournament_to_telegram, update_tournament_message, delete_tournament_message

def my_tournaments(request):
    tournaments = Tournament.objects.filter(organizer=request.user)
    return render(request, 'tournaments/my_tournaments.html', {'tournaments': tournaments})

def create_tournament(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        location = request.POST.get('location')
        format = request.POST.get('format')
        fee = request.POST.get('fee')
        level = request.POST.get('level')
        players_count = request.POST.get('players_count')
        tournament = Tournament.objects.create(
            name=name,
            date=date,
            location=location,
            format=format,
            fee=fee,
            level=level,
            players_count=players_count,
            organizer=request.user,
        )
        send_tournament_to_telegram(tournament, tournament.participants_through.all())
        return redirect('my_tournaments')
    return render(request, 'tournaments/create_tournament.html')

def join_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = request.user
    # используйте или создавайте User с реальными telegram_id и т.п.
    Participant.objects.get_or_create(tournament=tournament, user=user)
    participants = tournament.participants_through.all()
    update_tournament_message(tournament, participants)
    return redirect('my_tournaments')

def leave_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = request.user
    Participant.objects.filter(tournament=tournament, user=user).delete()
    participants = tournament.participants_through.all()
    update_tournament_message(tournament, participants)
    return redirect('my_tournaments')

def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    delete_tournament_message(tournament)
    tournament.delete()
    return redirect('my_tournaments')

def index(request):
    return render(request, "index.html")