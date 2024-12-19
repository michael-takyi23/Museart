from django import forms
from .models import Order


COUNTRY_CHOICES = [
    ('US', 'United States'),
    ('GB', 'United Kingdom'),
    ('GER', 'Germany'),
    ('FR', 'France'),
    ('IT', 'Italy'),
]

class OrderForm(forms.ModelForm):
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone_number', 'country', 'postcode',
                  'town_or_city', 'street_address1', 'street_address2']

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
            }),
            'postcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postcode',
            }),
            'town_or_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Town or City',
            }),
            'street_address1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address 1',
            }),
            'street_address2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address 2 (Optional)',
            }),
        }
