from django.db import models
from matches.models import Match

class Approved(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    approved_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Approved: {self.match}"
        