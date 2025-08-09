from django.db.models.signals import post_save
from django.dispatch import receiver
from matches.models import Match
from approved.models import Approved

@receiver(post_save, sender=Match)
def create_approved_on_status_change(sender, instance, created, **kwargs):
    # Only create Approved if status is 'approved'
    if instance.status == 'approved':
        # Get or create the Approved record linked to this match
        Approved.objects.get_or_create(match=instance)
    else:
        # Optionally: delete Approved record if status changed away from approved
        Approved.objects.filter(match=instance).delete()
