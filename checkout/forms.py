from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Order


class OrderForm(forms.ModelForm):
    """
    OrderForm handles checkout form inputs and auto-fills data for logged-in users.
    """

    country = CountryField(blank_label='Select Country').formfield(
        widget=CountrySelectWidget(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone_number', 'country', 'postcode',
            'town_or_city', 'street_address1', 'street_address2', 'county'
        ]

        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'pattern': "\\+?[0-9\\s-]+",
                'title': 'Enter a valid phone number',
                'required': True
            }),
            'postcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postcode'
            }),
            'town_or_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Town or City',
                'required': True
            }),
            'street_address1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address 1',
                'required': True
            }),
            'street_address2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address 2 (Optional)'
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'County/State (Optional)'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        Auto-fill user details if logged in.
        """
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['full_name'].initial = user.get_full_name()
            self.fields['email'].initial = user.email

    def clean_phone_number(self):
        """
        Custom validation for phone number format.
        """
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone
