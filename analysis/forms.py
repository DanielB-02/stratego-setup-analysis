from django import forms
from datetime import datetime

class FilterForm(forms.Form):
    RESULT_CHOICES = [
        ('', 'All Results'),
        ('win', 'Win'),
        ('draw', 'Draw'),
        ('loss', 'Loss'),
    ]
    
    NOOB_KILLER_CHOICES = [
        ('', 'All'),
        ('0', 'No'),
        ('1', 'Yes'),
    ]
    
    opponent = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter opponent name (optional)'
        })
    )
    
    result = forms.ChoiceField(
        choices=RESULT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    min_moves = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min moves'
        })
    )
    
    max_moves = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max moves'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    noob_killer = forms.ChoiceField(
        choices=NOOB_KILLER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

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