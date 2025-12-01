from django.contrib import admin
from django.urls import path, include
from tournaments.views import index, list_tournaments
from rest_framework import routers
from users.views import SportLevelViewSet

router = routers.DefaultRouter()
router.register(r'sportlevel', SportLevelViewSet, basename='sportlevel')

urlpatterns = [
    path("", index, name="home"),
    path("admin/", admin.site.urls),
    path("api/", include("tournaments.urls")),
    path('', include('users.urls')),
    path('list_tournaments/', list_tournaments, name='list_tournaments'),
    path('api/', include(router.urls)),
]
