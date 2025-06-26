from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
from .api.tasks import process_video

@receiver(post_save, sender=Video)
def trigger_processing(sender, instance, created, **kwargs):
    if created:
        process_video.delay(instance.id)
