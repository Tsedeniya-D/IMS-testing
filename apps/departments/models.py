from django.db import models

# Create your models here.


class Department(models.Model):
    department = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    intern_count = models.PositiveIntegerField()
    skills = models.TextField(blank=True, null=True)
    potential_project = models.TextField(blank=True, null=True)
     # Store field/count pairs as JSON: [{"field": "Physics", "count": 2}, ...]
    fields_and_counts = models.JSONField(default=list)
    submitted_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.department
