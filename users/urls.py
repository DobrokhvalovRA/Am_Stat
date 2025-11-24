from django.urls import path
from .views import TelegramLoginView, set_password, profile_view, logout_view, home

urlpatterns = [
    path('', home, name='home'),  # главная страница (если нужна)
    path('login/', TelegramLoginView.as_view(), name='login'),
    path('set-password/', set_password, name='set_password'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
]