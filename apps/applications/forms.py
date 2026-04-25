import re
from django import forms
from .models import InternshipApplication
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from datetime import date
import calendar


def add_months(source_date: date, months: int) -> date:
    month_index = source_date.month - 1 + months
    year = source_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

class InternshipApplicationForm(forms.ModelForm):
    phone = PhoneNumberField(region='ET',widget=forms.TextInput(attrs={
            'placeholder': '+2519XXXXXXXX',
            'value': '+251',  # shows +251 by default
        })
    )

    class Meta:
        model = InternshipApplication
        exclude = ['status', 'submitted_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional uploads in UX must be optional in backend too.
        self.fields['motivation_letter'].required = False
        self.fields['resume'].required = False
        # Filled conditionally in clean().
        self.fields['current_year'].required = False
        self.fields['expected_graduation'].required = False
        # Hidden/optional text fields should not block form validity.
        self.fields['interests'].required = False

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
        if not phone:
            raise ValidationError("Phone number is required.")

        # phonenumber_field gives a PhoneNumber object; normalize before regex.
        phone = str(phone).strip().replace(" ", "").replace("-", "")

        if not re.match(r'^\+251\d{9}$', phone):
            raise ValidationError("Invalid format. Use the Ethiopian format: +251XXXXXXXXX")

        return phone

    def clean_passport_id(self):
        file = self.cleaned_data.get('passport_id')
        if file and not file.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed.")
        return file

    def clean_motivation_letter(self):
        file = self.cleaned_data.get('motivation_letter')
        if file and not file.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed.")
        return file

    def clean_resume(self):
        file = self.cleaned_data.get('resume')
        if file and not file.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed.")
        return file

    def clean_recommendation_letter(self):
        file = self.cleaned_data.get('recommendation_letter')
        if file and not file.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF files are allowed.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        duration = cleaned_data.get('duration')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        education_level = str(
            cleaned_data.get('education_level', '')
        ).strip().lower()
        current_year = (cleaned_data.get('current_year') or '').strip()
        expected_graduation = (cleaned_data.get('expected_graduation') or '').strip()

        # Internship schedule fields should be all-or-none.
        if any([duration, start_date, end_date]) and not all([duration, start_date, end_date]):
            if not duration:
                self.add_error('duration', "Internship Duration is required.")
            if not start_date:
                self.add_error('start_date', "Start Date is required.")
            if not end_date:
                self.add_error('end_date', "End Date is required.")
        elif duration and start_date and end_date:
            try:
                duration_months = int(str(duration).split()[0])
            except (TypeError, ValueError, IndexError):
                self.add_error('duration', "Invalid duration format.")
                return cleaned_data

            expected_end_date = add_months(start_date, duration_months)
            if end_date != expected_end_date:
                # Keep server-side integrity while avoiding hard failure for minor client mismatch.
                cleaned_data['end_date'] = expected_end_date

        if education_level == 'graduate':
            cleaned_data['current_year'] = ''
            cleaned_data['expected_graduation'] = ''
        else:
            if not current_year:
                self.add_error('current_year', "Current Year of Study is required for non-graduate applicants.")
            if not expected_graduation:
                self.add_error('expected_graduation', "Expected Graduation is required for non-graduate applicants.")

        return cleaned_data