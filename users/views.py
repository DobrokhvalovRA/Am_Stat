from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TelegramLoginForm, PasswordCreationForm
from users.models import User, SportLevel
from participants.models import Participant
from django.views import View
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import viewsets
from .serializers import SportLevelSerializer


def home(request):
    return render(request, 'home.html')


class TelegramLoginView(View):
    template_name = "registration/login.html"
    max_attempts = 15  # Maximum login attempts
    lockout_duration = timedelta(minutes=15)  # Lockout duration after max attempts

    def _check_brute_force(self, request, identifier):
        session_key = f"login_attempts_{identifier}"
        lockout_key = f"lockout_until_{identifier}"


        lockout_until = request.session.get(lockout_key)
        if lockout_until:
            lockout_time = datetime.fromisoformat(lockout_until)
            if timezone.now() < lockout_time:
                remaining = (lockout_time - timezone.now()).seconds // 60
                return False, f"Слишком много попыток входа. Попробуйте через {remaining} минут"
            else:

                del request.session[lockout_key]
                request.session[session_key] = 0

        return True, None

    def _record_failed_attempt(self, request, identifier):
        """Record a failed login attempt"""
        session_key = f"login_attempts_{identifier}"
        lockout_key = f"lockout_until_{identifier}"

        attempts = request.session.get(session_key, 0) + 1
        request.session[session_key] = attempts

        if attempts >= self.max_attempts:
            lockout_until = timezone.now() + self.lockout_duration
            request.session[lockout_key] = lockout_until.isoformat()
            return f"Превышено количество попыток входа. Аккаунт заблокирован на {self.lockout_duration.seconds // 60} минут"

        return f"Неверные данные входа. Осталось попыток: , {self.max_attempts - attempts}"

    def _reset_attempts(self, request, identifier):

        session_key = f"login_attempts_{identifier}"
        lockout_key = f"lockout_until_{identifier}"

        if session_key in request.session:
            del request.session[session_key]
        if lockout_key in request.session:
            del request.session[lockout_key]

    def get(self, request):
        form = TelegramLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TelegramLoginForm(request.POST)
        if form.is_valid():
            telegram_id = form.cleaned_data.get("telegram_id")
            telegram_username = form.cleaned_data.get("telegram_username")
            password = form.cleaned_data.get("password")


            identifier = telegram_id or telegram_username


            can_attempt, error_msg = self._check_brute_force(request, identifier)
            if not can_attempt:
                return render(request, self.template_name, {
                    'form': form,
                    'error': error_msg
                })


            user = None
            if telegram_id:
                user = User.objects.filter(telegram_id=telegram_id).first()
            if not user and telegram_username:
                user = User.objects.filter(username=telegram_username).first()

            if not user:
                error_msg = self._record_failed_attempt(request, identifier)
                id_type = "Telegram ID" if telegram_id else "Telegram username"
                return render(request, self.template_name, {
                    'form': form,
                    'error': f"Пользователь с таким {id_type} не найден"
                })


            if not user.has_usable_password():
                login(request, user, backend='users.auth.TelegramBackend')


                self._reset_attempts(request, identifier)
                return redirect("create_password")


            user_auth = authenticate(
                request,
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                password=password
            )

            if user_auth:
                login(request, user_auth)
                self._reset_attempts(request, identifier)
                return redirect("profile")
            else:
                error_msg = self._record_failed_attempt(request, identifier)
                return render(request, self.template_name, {
                    'form': form,
                    'error': error_msg
                })

        return render(request, self.template_name, {'form': form})


@login_required
def create_password(request):
    user = request.user

    if user.has_usable_password():
        return redirect("profile")

    if request.method == "POST":
        form = PasswordCreationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()

            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно создан! Теперь вы можете входить используя Telegram ID и пароль.")
            return redirect("profile")
    else:
        form = PasswordCreationForm()

    return render(request, "registration/create_password.html", {'form': form})


@login_required
def set_password(request):
    user = request.user
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not password1 or password1 != password2:
            messages.error(request, "Пароли не совпадают")
        elif len(password1) < 8:
            messages.error(request, "Пароль слишком короткий (минимум 8 символов)")
        else:
            user.set_password(password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно установлен!")
            return redirect("profile")
    return render(request, "registration/create_password.html")


@login_required
def profile_view(request):
    user = request.user
    is_organizer = user.groups.filter(name="Организаторы турниров").exists()

    try:
        history = Participant.objects.filter(user=user).select_related('tournament')
    except (OperationalError, ProgrammingError):
        history = []

    sport_levels = SportLevel.objects.filter(user=user)

    if request.method == "POST":
        # Смена пароля
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if new_password:
            if len(new_password) < 8:
                messages.error(request, "Пароль должен содержать минимум 8 символов.")
            elif new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
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
        "sport_levels": sport_levels,
    })

class SportLevelViewSet(viewsets.ModelViewSet):
    queryset = SportLevel.objects.all()
    serializer_class = SportLevelSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user")
        sport_type = self.request.query_params.get("sport_type")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if sport_type:
            queryset = queryset.filter(sport_type=sport_type)
        return queryset

def logout_view(request):
    logout(request)
    return redirect('login')
