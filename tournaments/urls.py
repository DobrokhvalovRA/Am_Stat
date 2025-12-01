from django.urls import path
from rest_framework.routers import DefaultRouter
from .api_views import TournamentViewSet
from .views import (
    TournamentCreateView,
    TournamentHistoryView,
    TournamentUpdateView,
    TournamentDeleteView,
    join_tournament,
    leave_tournament,
    list_tournaments,
)

router = DefaultRouter()
router.register(r'tournaments', TournamentViewSet)

urlpatterns = [
    path("create/", TournamentCreateView.as_view(), name="create_tournament"),
    path("history/", TournamentHistoryView.as_view(), name="tournament_history"),
    path("edit/<int:pk>/", TournamentUpdateView.as_view(), name="edit_tournament"),
    path("delete/<int:pk>/", TournamentDeleteView.as_view(), name="delete_tournament"),
    path("join/<int:tournament_id>/", join_tournament, name="join_tournament"),
    path("leave/<int:tournament_id>/", leave_tournament, name="leave_tournament"),
    path('list_tournaments/', list_tournaments, name='list_tournaments'),
]

urlpatterns += router.urls