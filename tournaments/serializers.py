from rest_framework import serializers
from .models import Tournament
from participants.models import Participant

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'user', 'result']

class TournamentSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'date', 'location', 'format', 'fee', 'level', 'players_count', 'status', 'sport_type', 'organizer', 'participants']