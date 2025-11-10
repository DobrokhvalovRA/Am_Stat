
from rest_framework import serializers
from .models import Tournament, User
from participants.models import Participant

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "nickname", "telegram_id","phone_number")

class ParticipantSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    class Meta:
        model = Participant
        fields = ("id", "user", "result")

class TournamentSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True, source='participant_set')
    class Meta:
        model = Tournament
        fields = [ 'id', 'name', 'date', 'location', 'format', 'fee', 'level', 'players_count', 'tg_chat_id', 'tg_message_id', 'participants']