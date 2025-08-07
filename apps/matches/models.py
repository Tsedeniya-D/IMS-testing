from django.db import models
from django.utils import timezone
from apps.applications.models import InternshipApplication
from apps.departments.models import Department

class Match(models.Model):
    # Foreign keys to related models
    application = models.ForeignKey(
        InternshipApplication,
        on_delete=models.CASCADE,
        related_name='matched_departments'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='matched_applications'
    )

    # Denormalized fields for snapshot/reference
    student_name = models.CharField(max_length=100, blank=True, null=True)
    student_department = models.CharField(max_length=100, blank=True, null=True)
    student_skill = models.TextField(blank=True, null=True)

    institution_department = models.CharField(max_length=100, blank=True, null=True)
    fields_and_counts = models.JSONField(blank=True, null=True)
    department_skills = models.TextField(blank=True, null=True)
    department_additional_info = models.TextField(blank=True, null=True)

    # Status choices
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('waitlist', 'Waitlist'),
            ('rejected', 'Rejected'),
            ('approved', 'Approved')
        ],
        default='pending'
    )

    matched_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = ('application', 'department')

    def __str__(self):
        return f"{self.student_name} matched to {self.institution_department} ({self.status})"
