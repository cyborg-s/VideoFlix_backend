from rest_framework import serializers

from ..models import Video, VideoProgress
from .functions import get_video_by_resolution


class VideoUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading new video entries.

    Includes fields for ID, title, description, original file, and genre.
    """
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'original_file', 'genre']


class VideoListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing videos with summary information.

    Provides fields for ID, title, description, thumbnail, upload date, and genre.
    """
    class Meta:
        model = Video
        fields = ['id', 'title', 'description',
                  'thumbnail', 'upload_date', 'genre']


class VideoDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a video including multiple resolution URLs,
    thumbnail, genre, and user-specific last watched position.

    Provides read-only fields to retrieve URLs for different video resolutions,
    the preferred resolution, and the last watched playback position for
    authenticated users.
    """
    video_180p = serializers.SerializerMethodField()
    video_360p = serializers.SerializerMethodField()
    video_720p = serializers.SerializerMethodField()
    video_1080p = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    resolution = serializers.SerializerMethodField()
    last_position = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'description',
            'thumbnail',
            'genre',
            'video_180p',
            'video_360p',
            'video_720p',
            'video_1080p',
            'video_url',
            'resolution',
            'last_position',
        ]

    def get_video_180p(self, obj):
        """
        Return the absolute URL of the 180p resolution video file.
        """
        return self._get_video_url(obj, '180p')

    def get_video_360p(self, obj):
        """
        Return the absolute URL of the 360p resolution video file.
        """
        return self._get_video_url(obj, '360p')

    def get_video_720p(self, obj):
        """
        Return the absolute URL of the 720p resolution video file.
        """
        return self._get_video_url(obj, '720p')

    def get_video_1080p(self, obj):
        """
        Return the absolute URL of the 1080p resolution video file.
        """
        return self._get_video_url(obj, '1080p')

    def get_resolution(self, obj):
        """
        Return the preferred video resolution as a string.

        Currently hardcoded to '720p'.
        """
        return '720p'

    def get_video_url(self, obj):
        """
        Return the absolute URL of the preferred resolution video file.

        Uses 720p as the preferred resolution.
        """
        request = self.context.get('request')
        video_file = get_video_by_resolution(obj, '720p')
        if video_file and hasattr(video_file, 'url'):
            return request.build_absolute_uri(video_file.url) if request else video_file.url
        return None

    def get_last_position(self, obj):
        """
        Retrieve the last watched playback position in seconds for the
        authenticated user and the given video.

        Returns 0 if no progress is recorded or user is anonymous.
        """
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            progress = VideoProgress.objects.filter(
                user=user, video=obj).first()
            if progress:
                return progress.position_in_seconds
        return 0

    def _get_video_url(self, obj, resolution):
        """
        Helper method to get the absolute URL for a given video resolution.

        Args:
            obj: Video instance.
            resolution (str): Resolution key (e.g., '180p', '360p', etc.).

        Returns:
            str or None: Absolute URL of the video file or None if unavailable.
        """
        request = self.context.get('request')
        video_file = get_video_by_resolution(obj, resolution)
        if video_file and hasattr(video_file, 'url'):
            return request.build_absolute_uri(video_file.url) if request else video_file.url
        return None
