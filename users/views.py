from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import TelegramLoginForm
from django.contrib.auth import logout
from users.models import User
from participants.models import Participant
from django.contrib.auth import authenticate, login

def home(request):
    return render(request, 'home.html')

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import TelegramLoginForm

class TelegramLoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        form = TelegramLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TelegramLoginForm(request.POST)
        if form.is_valid():
            telegram_id = form.cleaned_data.get("telegram_id")
            telegram_username = form.cleaned_data.get("telegram_username")
            password = form.cleaned_data.get("password")

            print(telegram_username)
            user = User.objects.filter(telegram_id__iexact="591768306")
            print(user)

            user = authenticate(
                request,
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                password=password
            )
            print("User found:", user)
            if user:
                login(request, user)
                return redirect("profile")  # поменяй на нужный url
            else:
                return render(request, self.template_name, {'form': form, 'error': "Неверные данные входа"})
        return render(request, self.template_name, {'form': form})

@login_required
def set_password(request):
    user = request.user
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if not password1 or password1 != password2:
            messages.error(request, "Пароли не совпадают")
        elif len(password1) < 6:
            messages.error(request, "Пароль слишком короткий (минимум 6 символов)")
        else:
            user.set_password(password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно установлен!")
            return redirect("/")
    return render(request, "registration/set_password.html")

@login_required
def profile_view(request):
    user = request.user

    # Получаем связанные записи участника
    history = Participant.objects.filter(user=user).select_related('tournament')

    if request.method == "POST":
        # Смена пароля
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if new_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Пароль успешно изменён.")
                # После смены пароля нужно заново авторизовать пользователя (опционально)
                # from django.contrib.auth import update_session_auth_hash
                # update_session_auth_hash(request, user)
            else:
                messages.error(request, "Пароли не совпадают.")

    # Обработка изменения профиля
    if request.method == "POST":
        user.nickname = request.POST.get("nickname", user.nickname)
        user.phone = request.POST.get("phone", user.phone)
        user.photo = request.FILES.get("photo", user.photo)
        user.save()
        return redirect('profile')



    return render(request, "users/profile.html", {
        "user": user,
        "history": history,

    })

def logout_view(request):
    logout(request)
    return redirect('login')

