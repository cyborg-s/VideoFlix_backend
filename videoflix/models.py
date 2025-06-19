from django.db import models
from django.conf import settings


class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    original_file = models.FileField(
        upload_to='videos/original/', max_length=255)
    thumbnail = models.ImageField(
        upload_to='videos/thumbnails/', max_length=255)

    video_180p = models.FileField(
        upload_to='videos/180p/', null=True, blank=True, max_length=255)
    video_360p = models.FileField(
        upload_to='videos/360p/', null=True, blank=True, max_length=255)
    video_720p = models.FileField(
        upload_to='videos/720p/', null=True, blank=True, max_length=255)
    video_1080p = models.FileField(
        upload_to='videos/1080p/', null=True, blank=True, max_length=255)

    upload_date = models.DateTimeField(auto_now_add=True)

    GENRE_CHOICES = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('documentary', 'Documentary'),
        ('horror', 'Horror'),
        ('sci-fi', 'Science Fiction'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('animation', 'Animation'),
        ('fantasy', 'Fantasy'),
    ]
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)

    def __str__(self):
        return self.title


class VideoProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    position_in_seconds = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} - {self.video.title} ({self.position_in_seconds}s)"
