from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    allowed_levels = forms.MultipleChoiceField(
        choices=Tournament.LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Подходящие уровни"
    )
    class Meta:
        model = Tournament
        fields = [
            "name", "date", "allowed_levels",
            # все остальные поля которые есть в модели Tournament
        ]
"""from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'date', 'location', 'format', 'fee', 'level', 'players_count', 'sport_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'fee': forms.NumberInput(attrs={'step': '0.01'}),
        }"""