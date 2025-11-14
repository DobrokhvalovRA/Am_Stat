from django.contrib.auth.backends import ModelBackend
from users.models import User

class TelegramIDBackend(ModelBackend):
    def authenticate(self, request, telegram_id=None, password=None, **kwargs):
        if telegram_id is None:
            return None
        try:
            user = User.objects.get(telegram_id=telegram_id)
            if user.has_usable_password():
                # вход с паролем
                if password and user.check_password(password):
                    return user
            else:
                # вход без пароля только по telegram_id (первый вход)
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None