from rest_framework import serializers
from .models import Participant
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "nickname", "telegram_id","rating")

class ParticipantSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Participant
        fields = ('id', 'user', 'result')

