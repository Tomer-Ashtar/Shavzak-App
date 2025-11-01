from django import forms
from .models import Worker


class WorkerForm(forms.ModelForm):
    """Form for creating and updating workers."""
    
    class Meta:
        model = Worker
        fields = ['name', 'title', 'hard_chores_counter', 'outer_partner_counter']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter worker name'}),
            'title': forms.Select(attrs={'class': 'form-control'}),
            'hard_chores_counter': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'outer_partner_counter': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
        help_texts = {
            'hard_chores_counter': 'Number of hard chores completed (e.g., kitchen duty)',
            'outer_partner_counter': 'Number of outer partner assignments completed',
        }

