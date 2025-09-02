from django import forms
from .models import VolunteerSignup

class VolunteerSignupForm(forms.ModelForm):
    class Meta:
        model = VolunteerSignup
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name', 'id': 'name-field'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com', 'id': 'email-field'}),
        }
