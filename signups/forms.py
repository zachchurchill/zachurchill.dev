from django import forms
from .models import VolunteerSignup, Family

class VolunteerSignupForm(forms.ModelForm):
    family_choice = forms.ChoiceField(
        required=False,
        choices=[('', '-- Select a family or enter manually --')],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'family-select'})
    )
    
    class Meta:
        model = VolunteerSignup
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name', 'id': 'name-field'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com', 'id': 'email-field'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get active families for the dropdown
        families = Family.objects.filter(is_active=True).order_by('last_name')
        family_choices = [('', '-- Select a family or enter manually --')]
        family_choices.extend([(family.id, f"{family.last_name} Family") for family in families])
        self.fields['family_choice'].choices = family_choices
