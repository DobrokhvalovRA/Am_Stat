from rest_framework import serializers
from .models import SportLevel

class SportLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportLevel
        fields = "__all__"