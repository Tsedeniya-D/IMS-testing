from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class InternshipApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('application', 'Application Submitted'),
        ('review', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('approval', 'Approved'),
    ]
    name_validator = RegexValidator(
        regex=r'^[a-zA-Z\s]*$',
        message="Name must only contain letters and spaces.",
        code='invalid_name'
    )
    first_name = models.CharField(max_length=20, validators=[name_validator],help_text="Enter your full legal name (Letters only)")
    last_name = models.CharField(max_length=20, validators=[name_validator],help_text="Enter your full legal name (Letters only)")
    age = models.IntegerField(null=True, blank=True)



    email = models.EmailField()
    phone = PhoneNumberField(region='ET')
    city = models.CharField(max_length=100)
    university = models.CharField(max_length=200, blank=True, null=True)
    college_name = models.CharField(max_length=200, blank=True, null=True)
    nationality = models.CharField(max_length=100, default='Not Provided')
    address = models.CharField(max_length=200, default='Not Provided')
    education_level = models.CharField(max_length=50, default='Not Provided')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    passport_id = models.FileField(upload_to='passport_ids/',validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    department = models.CharField(max_length=100, default='Not Provided')
    current_year = models.CharField(max_length=10, default='Not Provided')
    expected_graduation = models.CharField(max_length=20, default='Not Provided')
    duration = models.CharField(max_length=10, choices=[(f"{i} month", f"{i} month{'s' if i > 1 else ''}") for i in range(1, 13)], null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    skills = models.TextField(blank=True, default='Not Provided')
    interests = models.TextField(default='Not Provided')
    motivation_letter = models.FileField(upload_to='motivation_letters/',validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    resume = models.FileField(upload_to='resumes/',validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    recommendation_letter = models.FileField(upload_to='recommendations/',validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
def duration_display(self):
    if self.duration:
        num = int(self.duration.split()[0])
        return f"{num} month{'s' if num > 1 else ''}"
    return ""

