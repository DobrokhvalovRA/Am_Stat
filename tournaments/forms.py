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
            'name', 'date', 'location', 'format', 'fee', "allowed_levels",'players_count', 'sport_type'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'fee': forms.NumberInput(attrs={'step': '50.'}),
            "sport_type": forms.Select(),
        }
