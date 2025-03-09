from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
    Form for updating the user's profile information.
    - Excludes the `user` field since it should not be changed manually.
    - Adds placeholders for better UX.
    - Uses Bootstrap-friendly classes for styling.
    """
    class Meta:
        model = UserProfile
        exclude = ('user',)  # Prevent editing the associated user directly

    def __init__(self, *args, **kwargs):
        """
        Customize form fields:
        - Add placeholders for better user guidance.
        - Apply Bootstrap and custom classes for styling.
        - Remove labels to create a cleaner UI.
        - Set autofocus on the first field.
        """
        super().__init__(*args, **kwargs)

        placeholders = {
            'default_phone_number': '📞 Phone Number',
            'default_postcode': '📮 Postal Code',
            'default_town_or_city': '🏙️ Town or City',
            'default_street_address1': '🏠 Street Address 1',
            'default_street_address2': '🏠 Street Address 2 (Optional)',
            'default_county': '🌍 County, State or Locality',
        }

        # Set autofocus on the first field
        self.fields['default_phone_number'].widget.attrs['autofocus'] = True

        for field in self.fields:
            if field != 'default_country':  # Country field uses a dropdown
                placeholder = placeholders.get(field, '')
                if self.fields[field].required:
                    placeholder += " *"  # Indicate required fields
                self.fields[field].widget.attrs['placeholder'] = placeholder

            # Apply Bootstrap and custom styling
            self.fields[field].widget.attrs['class'] = (
                'form-control border-black rounded-0 profile-form-input'
            )

            # Hide field labels (cleaner UI)
            self.fields[field].label = False
