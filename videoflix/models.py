"""
Defines the data models for videos and video playback progress.

Classes:
    Video: Represents a video with metadata, different resolution files, and genre.
    VideoProgress: Tracks the playback position of a user for a specific video.
"""

from django.db import models
from django.conf import settings


class Video(models.Model):
    """
    Model representing a video entity.

    Attributes:
        title (CharField): The title of the video.
        description (TextField): A detailed description of the video content.
        original_file (FileField): The original uploaded video file.
        thumbnail (ImageField): The thumbnail image for the video.
        video_180p (FileField): The video file at 180p resolution (optional).
        video_360p (FileField): The video file at 360p resolution (optional).
        video_720p (FileField): The video file at 720p resolution (optional).
        video_1080p (FileField): The video file at 1080p resolution (optional).
        upload_date (DateTimeField): Timestamp when the video was uploaded.
        genre (CharField): The genre/category of the video, selected from predefined choices.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    original_file = models.FileField(
        upload_to='videos/original/', max_length=255)
    thumbnail = models.ImageField(
        upload_to='videos/thumbnails/', max_length=255 , null=True, blank=True)

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
        """
        Returns a string representation of the Video instance.

        Returns:
            str: The title of the video.
        """
        return self.title


class VideoProgress(models.Model):
    """
    Model to track the playback progress of a user for a specific video.

    Attributes:
        user (ForeignKey): Reference to the user who is watching the video.
        video (ForeignKey): Reference to the video being watched.
        position_in_seconds (FloatField): The last watched position in seconds.
        updated_at (DateTimeField): Timestamp of the last progress update.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    position_in_seconds = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for VideoProgress model.

        Enforces uniqueness on the combination of user and video.
        """
        unique_together = ('user', 'video')

    def __str__(self):
        """
        Returns a string representation of the VideoProgress instance.

        Returns:
            str: A string indicating the user, video title, and position in seconds.
        """
        return f"{self.user.username} - {self.video.title} ({self.position_in_seconds}s)"
