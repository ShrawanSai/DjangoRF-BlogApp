from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Invitation, Event



@receiver(post_save, sender=Event)
def create_invitation(sender, instance, created, **kwargs):
    if created:
        Invitation.objects.create(event=instance)


# @receiver(post_save, sender=Event)
# def save_invitation(sender, instance, **kwargs):
#     print(instance)
#     instance.invitation.save()