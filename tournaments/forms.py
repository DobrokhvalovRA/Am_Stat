from django import forms
from django.core.exceptions import ValidationError
from .models import Tournament

class TournamentForm(forms.ModelForm):
    allowed_levels = forms.MultipleChoiceField(
        choices=Tournament.LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Допустимые уровни"
    )
    name = forms.CharField(required=True, label="Название турнира")
    date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label="Дата проведения")
    location = forms.CharField(required=True, label="Место проведения")
    format = forms.ChoiceField(required=True, label="Формат", choices=Tournament.FORMAT_CHOICES)
    fee = forms.IntegerField(required=True, label="Взнос", widget=forms.NumberInput(attrs={'step': '50'}))
    players_count = forms.ChoiceField(required=True, label="Кол-во игроков", choices=[(4, 4), (8, 8), (12, 12), (16, 16)])
    sport_type = forms.ChoiceField(required=True, label="Вид спорта", choices=Tournament.SPORT_TYPE_CHOICES)
    class Meta:
        model = Tournament
        fields = [
            'name', 'date', 'location', 'format', 'fee', 'allowed_levels', 'players_count', 'sport_type'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # При редактировании, чтобы показать уже выбранные уровни
        if self.instance and self.instance.pk:
            self.fields['allowed_levels'].initial = self.instance.level
    
    def clean_format(self):
        format = self.cleaned_data.get('format')
        if (format != 'solo'):
            raise ValidationError("Пока поддерживаются только одиночные турниры" )
        return format

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Сохраняем выбранные уровни из allowed_levels в level (модель Tournament)
        instance.level = self.cleaned_data['allowed_levels']
        if commit:
            instance.save()
        return instance