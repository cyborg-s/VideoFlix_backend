from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video


@receiver(post_save, sender=Video)
def create_lecture(sender, instance, created, **kwargs):
    if created:
        print('New object created')