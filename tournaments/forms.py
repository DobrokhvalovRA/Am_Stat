from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    allowed_levels = forms.MultipleChoiceField(
        choices=Tournament.LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Допустимые уровни"
    )
    class Meta:
        model = Tournament
        fields = [
            'name', 'date', 'location', 'format', 'fee', 'allowed_levels', 'players_count', 'sport_type'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'fee': forms.NumberInput(attrs={'step': '50.'}),
            'sport_type': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # При редактировании, чтобы показать уже выбранные уровни
        if self.instance and self.instance.pk:
            self.fields['allowed_levels'].initial = self.instance.level

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Сохраняем выбранные уровни из allowed_levels в level (модель Tournament)
        instance.level = self.cleaned_data['allowed_levels']
        if commit:
            instance.save()
        return instance