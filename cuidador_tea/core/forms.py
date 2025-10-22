# core/forms.py

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'data_nascimento', 'grau_autismo', 'tem_laudo']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }