from django.db import IntegrityError
from participants.models import Participant

def SaveTour(tourDto, tournament):
    try:
        tour = tournament.tour_set.create(number = tourDto.number)
        for matchDto in tourDto.matches:
            match = tour.match_set.create()
            _saveTeamComposition(match, 1, matchDto.teamA)
            _saveTeamComposition(match, 2, matchDto.teamB)
    except IntegrityError:
        print("An error occurred, transaction rolled back.")

def _saveTeamComposition(match, teamNumber, teamComposition):
    player1 = Participant.objects.select_related().get(id=teamComposition.player1.participantId)
    player2 = Participant.objects.select_related().get(id=teamComposition.player2.participantId)
    match.teamcomposition_set.create(teamNumber = teamNumber, player1 = player1, player2 = player2)