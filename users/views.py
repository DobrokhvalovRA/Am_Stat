from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TelegramLoginForm, PasswordCreationForm
from users.models import User
from participants.models import Participant
from django.views import View
from django.utils import timezone
from datetime import timedelta

def home(request):
    return render(request, 'home.html')

class TelegramLoginView(View):
    template_name = "registration/login.html"
    max_attempts = 5  # Maximum login attempts
    lockout_duration = timedelta(minutes=15)  # Lockout duration after max attempts

    def _check_brute_force(self, request, identifier):
        """Check if the user/IP has exceeded login attempts"""
        session_key = f"login_attempts_{identifier}"
        lockout_key = f"lockout_until_{identifier}"
        
        # Check if currently locked out
        lockout_until = request.session.get(lockout_key)
        if lockout_until:
            lockout_time = timezone.datetime.fromisoformat(lockout_until)
            if timezone.now() < lockout_time:
                remaining = (lockout_time - timezone.now()).seconds // 60
                return False, f"Слишком много попыток входа. Попробуйте через {remaining} минут"
            else:
                # Lockout expired, reset
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
        
        return f"Неверные данные входа. Осталось попыток: {self.max_attempts - attempts}"

    def _reset_attempts(self, request, identifier):
        """Reset login attempts after successful login"""
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

            # Use telegram_id or username as identifier for brute force protection
            identifier = telegram_id or telegram_username
            
            # Check brute force protection
            can_attempt, error_msg = self._check_brute_force(request, identifier)
            if not can_attempt:
                return render(request, self.template_name, {
                    'form': form,
                    'error': error_msg
                })

            # Try to find the user
            user = None
            if telegram_id:
                user = User.objects.filter(telegram_id=telegram_id).first()
            elif telegram_username:
                user = User.objects.filter(username=telegram_username).first()

            # If user not found
            if not user:
                error_msg = self._record_failed_attempt(request, identifier)
                return render(request, self.template_name, {
                    'form': form,
                    'error': "Пользователь с таким Telegram ID не найден"
                })

            # Check if user has a password set
            if not user.has_usable_password():
                # First-time user - show password creation form
                login(request, user, backend='users.auth.TelegramBackend')
                self._reset_attempts(request, identifier)
                return redirect("create_password")

            # User has password - authenticate with password
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
    """
    View for first-time users to create a password.
    This is called when a user logs in with Telegram ID but doesn't have a password yet.
    """
    user = request.user
    
    # If user already has a password, redirect to profile
    if user.has_usable_password():
        return redirect("profile")
    
    if request.method == "POST":
        form = PasswordCreationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password1")
            user.set_password(password)
            user.save()
            # Keep user logged in after setting password
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно создан! Теперь вы можете входить используя Telegram ID и пароль.")
            return redirect("profile")
    else:
        form = PasswordCreationForm()
    
    return render(request, "registration/create_password.html", {'form': form})

@login_required
def set_password(request):
    """
    View for changing/setting password from profile page.
    Enhanced with better validation (minimum 8 characters).
    """
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
    return render(request, "registration/set_password.html")

@login_required
def profile_view(request):
    user = request.user
    is_organizer = user.groups.filter(name="Организаторы турниров").exists()
    
    # Try to get participant history, but handle if the table doesn't exist (e.g., during tests)
    try:
        history = Participant.objects.filter(user=user).select_related('tournament')
    except Exception:
        history = []

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
    })

def logout_view(request):
    logout(request)
    return redirect('login')