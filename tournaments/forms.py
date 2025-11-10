from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'date', 'location', 'format', 'fee', 'level', 'players_count', 'sport_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'fee': forms.NumberInput(attrs={'step': '0.01'}),
        }