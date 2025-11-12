from django.shortcuts import render, redirect, get_object_or_404
from tournaments.models import Tournament, User
from participants.models import Participant
from .telegram_notify import send_tournament_to_telegram, delete_tournament_message
from .forms import TournamentForm



def create_tournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            return redirect('tournaments:my_tournaments')
    else:
        form = TournamentForm()
    return render(request, 'tournaments/create_tournament.html', {'form': form})

def edit_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect('tournaments:my_tournaments')
    else:
        form = TournamentForm(instance=tournament)
    return render(request, 'tournaments/tournament_edit.html', {'form': form})


def join_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = request.user
    # используйте или создавайте User с реальными telegram_id и т.п.
    Participant.objects.get_or_create(tournament=tournament, user=user)
    return redirect('my_tournaments')

def leave_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = request.user
    Participant.objects.filter(tournament=tournament, user=user).delete()
    return redirect('my_tournaments')

def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    delete_tournament_message(tournament)
    tournament.delete()
    return redirect('my_tournaments')

"""def edit_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == 'POST':
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            return redirect('tournaments:my_tournaments')
    else:
        form = TournamentForm(instance=tournament)
    return render(request, 'tournaments/tournament_edit.html', {'form': form})"""

def index(request):
    return render(request, "index.html")