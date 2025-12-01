from django.urls import path
from .views import TelegramLoginView, create_password, set_password, profile_view, logout_view, home

urlpatterns = [
    path('', home, name='home'),  # главная страница (если нужна)
    path('login/', TelegramLoginView.as_view(), name='login'),
    path('create-password/', create_password, name='create_password'),

    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout')]