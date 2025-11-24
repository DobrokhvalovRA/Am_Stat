from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TelegramLoginForm
from users.models import User
from participants.models import Participant
from django.views import View

def home(request):
    return render(request, 'home.html')

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

            # Кастомная аутентификация
            user_auth = authenticate(
                request,
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                password=password
            )

            if user_auth:
                login(request, user_auth)
                # Если у пользователя нет пароля, предлагаем его создать
                if not user_auth.has_usable_password():
                    return redirect("set_password")
                return redirect("profile")
            else:
                return render(request, self.template_name, {
                    'form': form,
                    'error': "Неверные данные входа"
                })
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
            return redirect("profile")
    return render(request, "registration/set_password.html")

@login_required
def profile_view(request):
    user = request.user
    is_organizer = user.groups.filter(name="Организаторы турниров").exists()
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
            else:
                messages.error(request, "Пароли не совпадают.")

        # Обработка изменения профиля
        user.nickname = request.POST.get("nickname", user.nickname)
        user.phone = request.POST.get("phone", user.phone)
        photo_file = request.FILES.get("photo")
        if photo_file:
            user.photo = photo_file
        user.save()
        return redirect('profile')

    return render(request, "users/profile.html", {
        "user": user,
        "history": history,
        "is_organizer": is_organizer,
    })

def logout_view(request):
    logout(request)
    return redirect('login')