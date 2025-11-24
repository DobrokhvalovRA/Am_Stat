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
            'name', 'date', 'location', 'format', 'fee', "allowed_levels","players_count", 'sport_type'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'fee': forms.NumberInput(attrs={'step': '50.'}),
            'sport_type': forms.Select(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # начальное значение для allowed_levels
        if self.instance and self.instance.pk:
            self.fields['allowed_levels'].initial = self.instance.level

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.level = self.cleaned_data['allowed_levels']
        if commit:
            instance.save()
        return instance

"""from django import forms
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
"""