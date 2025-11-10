from rest_framework import viewsets
from .models import Tournament
from .serializers import TournamentSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]