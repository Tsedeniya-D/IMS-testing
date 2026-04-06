import re
from django import forms
from .models import InternshipApplication
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField

class InternshipApplicationForm(forms.ModelForm):
    phone = PhoneNumberField(region='ET',widget=forms.TextInput(attrs={
            'placeholder': '+2519XXXXXXXX',
            'value': '+251',  # shows +251 by default
        })
    )

    class Meta:
        model = InternshipApplication
        fields = '__all__'

    # GUARD 1: Letters Only & Max 20 for First Name
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z\s]*$', first_name):
            raise ValidationError("First name must only contain letters.")
        if len(first_name) > 20:
            raise ValidationError("First name cannot exceed 20 characters.")
        return first_name

    # GUARD 2: Letters Only & Max 20 for Last Name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z\s]*$', last_name):
            raise ValidationError("Last name must only contain letters.")
        if len(last_name) > 20:
            raise ValidationError("Last name cannot exceed 20 characters.")
        return last_name

    # GUARD 3: Ethiopian Phone Standard (+251)
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Standardize: remove spaces or dashes
        phone = phone.replace(" ", "").replace("-", "")
        
        # Regex check for +251 followed by 9 digits
        if not re.match(r'^\+251\d{9}$', phone):
            raise ValidationError("Invalid format. Use the Ethiopian format: +251XXXXXXXXX")
        
        return phone
    def clean_motivation_letter(self):
        file = self.cleaned_data.get('motivation_letter')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise ValidationError("Motivation letter must be a PDF.")
        return file

    def clean_resume(self):
        file = self.cleaned_data.get('resume')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise ValidationError("Resume must be a PDF.")
        return file

    def clean_recommendation_letter(self):
        file = self.cleaned_data.get('recommendation_letter')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise ValidationError("Recommendation letter must be a PDF.")
        return file