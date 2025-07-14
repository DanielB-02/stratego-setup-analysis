from django import forms
from datetime import datetime

class SetupForm(forms.Form):
    RESULT_CHOICES = [
        ('win', 'Win'),
        ('draw', 'Draw'),
        ('loss', 'Loss'),
    ]
    
    NOOB_KILLER_CHOICES = [
        (0, 'No'),
        (1, 'Yes'),
    ]
    
    date_played = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        initial=datetime.now().date()
    )
    
    opponent_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter opponent name'
        })
    )
    
    result = forms.ChoiceField(
        choices=RESULT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    moves = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Number of moves'
        })
    )
    
    noob_killer = forms.ChoiceField(
        choices=NOOB_KILLER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    setup_image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )