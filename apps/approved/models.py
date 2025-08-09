from django.db import models
from matches.models import Match

class Approved(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    approved_on = models.DateTimeField(auto_now_add=True)
    registered = models.BooleanField(default=False)
    
    # Snapshot fields to store student name and department name
    student_name = models.CharField(max_length=255, blank=True)
    department_name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        # Populate snapshot fields from related Match and Application on creation
        if not self.pk:  # only on first save (creation)
            student = self.match.application
            dept = self.match.department
            self.student_name = f"{student.first_name} {student.last_name}"
            self.department_name = dept.department
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Approved: {self.student_name} - Department: {self.department_name} - Registered: {self.registered}"
