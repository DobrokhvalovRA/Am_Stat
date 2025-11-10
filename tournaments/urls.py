from rest_framework.routers import DefaultRouter
from .api_views import TournamentViewSet

router = DefaultRouter()
router.register(r'tournaments', TournamentViewSet)

urlpatterns = router.urls