from django import forms
from django.core.exceptions import ValidationError
from users.models import User

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


class PasswordCreationForm(forms.Form):
    """Form for creating a password for first-time users"""
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'minlength': '8'}),
        min_length=8,
        help_text="Минимум 8 символов"
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'minlength': '8'}),
        min_length=8,
        help_text="Введите пароль повторно"
    )

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        
        return cleaned_data




