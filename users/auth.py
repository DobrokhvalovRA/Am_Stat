from django.contrib.auth.backends import ModelBackend
from users.models import User

class TelegramBackend(ModelBackend):
    def authenticate(self, request, telegram_id=None, telegram_username=None, password=None, **kwargs):
        user = None
        if telegram_id:
            user = User.objects.filter(telegram_id=telegram_id).first()
        if not user and telegram_username:
            user = User.objects.filter(username=telegram_username).first()
        if user:
            if user.has_usable_password():
                # если пароль установлен, проверяй по паролю
                if password and user.check_password(password):
                    return user
            else:
                # если пароля нет — логинить только по id/username
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None