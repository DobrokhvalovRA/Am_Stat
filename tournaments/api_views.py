from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tournament
from .serializers import TournamentSerializer
from participants.models import Participant
from participants.serializers import ParticipantSerializer
from users.models import User
from rest_framework import status

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        tournament = self.get_object()
        telegram_id = request.data.get('telegram_id')
        username = request.data.get('username')
        user, created = User.objects.get_or_create(telegram_id=telegram_id, defaults={'username':username})
        if not Participant.objects.filter(tournament=tournament, user=user).exists():
            Participant.objects.create(tournament=tournament, user=user)
            return Response({"status": "joined"}, status=201)
        else:
            return Response({"error": "already joined"}, status=400)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        tournament = self.get_object()
        telegram_id = request.data.get('telegram_id')
        try:
            user = User.objects.get(telegram_id=telegram_id)
            Participant.objects.filter(tournament=tournament, user=user).delete()
            return Response({"status": "left"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "user not found"}, status=404)