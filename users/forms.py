from django import forms

class TelegramLoginForm(forms.Form):
    telegram_id = forms.CharField(required=False, label="Telegram ID")
    telegram_username = forms.CharField(required=False, label="Telegram Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль (если установлен)", required=False)

    def clean(self):
        cleaned_data = super().clean()
        telegram_id = cleaned_data.get("telegram_id")
        telegram_username = cleaned_data.get("telegram_username")
        if not telegram_id and not telegram_username:
            raise forms.ValidationError("Укажите Telegram ID или Username")
        return cleaned_data
    def __init__(self, *args, **kwargs):
        # Accept request kwarg for compatibility with Django LoginView
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)




