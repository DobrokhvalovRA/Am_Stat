from django import forms

class TelegramLoginForm(forms.Form):
    telegram_id = forms.CharField(label="Telegram ID")
    password = forms.CharField(label="Пароль", required=False, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        # Accept request kwarg for compatibility with Django LoginView
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)