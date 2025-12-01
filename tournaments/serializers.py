from rest_framework import serializers
from .models import Tournament
from participants.models import Participant
from users.models import User, SportLevel

class UserProfileSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "username", "first_name", "last_name", "nickname", "telegram_id", "phone", "level", "rating"
        )

    def get_level(self, obj):
        sport_type = self.context.get('sport_type')
        if sport_type:
            sport_level = SportLevel.objects.filter(user=obj, sport_type=sport_type).first()
            return sport_level.level if sport_level else None
        return None

    def get_rating(self, obj):
        sport_type = self.context.get('sport_type')
        if sport_type:
            sport_level = SportLevel.objects.filter(user=obj, sport_type=sport_type).first()
            return sport_level.rating if sport_level else None
        return None

class ParticipantSerializer(serializers.ModelSerializer):
    # Передаем context через UserProfileSerializer автоматически
    # В TournamentSerializer при инициализации тоже нужно передать sport_type для вложенных сериализаторов!
    user = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ("id", "user", "result")

    def get_user(self, obj):
        # Текущий sport_type можно получить из tournament, если participant связан
        tournament = getattr(obj, "tournament", None)
        sport_type = tournament.sport_type if tournament else None
        context = self.context.copy()
        if sport_type:
            context['sport_type'] = sport_type
        return UserProfileSerializer(obj.user, context=context).data

class TournamentSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True, source='participant_set')

    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'date', 'location', 'format', 'fee', 'level',
            'players_count', 'tg_chat_id', 'tg_message_id', 'participants', 'sport_type'
        ]

"""from rest_framework import serializers
from .models import Tournament
from participants.models import Participant
from users.models import User, SportLevel

class UserProfileSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "nickname", "telegram_id", "phone")

class ParticipantSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    class Meta:
        model = Participant
        fields = ("id", "user", "result")

class TournamentSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True, source='participant_set')
    class Meta:
        model = Tournament
        fields = [
            'id', 'name', 'date', 'location', 'format', 'fee', 'level', 'players_count',
            'tg_chat_id', 'tg_message_id', 'participants', 'sport_type'
        ]"""

