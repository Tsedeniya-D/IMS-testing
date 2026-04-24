from django.db import models
from django.utils import timezone

# Create your models here.


# Simple DepartmentUser model for admin management and custom login
# class DepartmentUser(models.Model):
#     email = models.EmailField(unique=True)
#     department = models.CharField(max_length=255)
#     password = models.CharField(max_length=128)
#     is_active = models.BooleanField(default=True)
#     date_joined = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.email} ({self.department})"


class Department(models.Model):
    department = models.CharField(max_length=255)
    intern_count = models.PositiveIntegerField()
    skills = models.TextField(blank=True, null=True)
    potential_project = models.TextField(blank=True, null=True)
    mentor = models.CharField(max_length=20, blank=True, null=True)
    fields_and_counts = models.JSONField(default=list)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.department

    def clean(self):
        from django.core.exceptions import ValidationError
        import re
        
        if self.intern_count < 1:
            raise ValidationError('Intern count must be 1 or above. Negative numbers and 0 are not allowed.')
        if self.mentor and len(self.mentor) > 20:
            raise ValidationError('Mentor name must be maximum 20 characters long.')
        
        # Validate skills field - only allow letters and spaces (like mentor name)
        if self.skills:
            skills_pattern = re.compile(r'^[a-zA-Z\s]+$')
            if not skills_pattern.match(self.skills):
                raise ValidationError('Skills field should only contain letters and spaces.')
        
        # Validate potential project field - only allow letters and spaces (like mentor name)
        if self.potential_project:
            project_pattern = re.compile(r'^[a-zA-Z\s]+$')
            if not project_pattern.match(self.potential_project):
                raise ValidationError('Potential project field should only contain letters and spaces.')


class DepartmentPortalConfig(models.Model):
    is_open = models.BooleanField(default=False, help_text="Master switch for the Departments portal.")
    open_from = models.DateTimeField(null=True, blank=True, help_text="Optional start date/time.")
    open_until = models.DateTimeField(null=True, blank=True, help_text="Optional end date/time.")

    class Meta:
        verbose_name = "Departments portal config"
        verbose_name_plural = "Departments portal config"

    def __str__(self):
        return "Departments Portal Config"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def is_within_window(self, now=None):
        now = now or timezone.now()
        if self.open_from and now < self.open_from:
            return False
        if self.open_until and now > self.open_until:
            return False
        return True

    @property
    def is_effectively_open(self):
        return self.is_open and self.is_within_window()
