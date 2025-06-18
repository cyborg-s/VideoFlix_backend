# videoflix/api/serializers.py
from rest_framework import serializers
from ..models import Video, VideoProgress
from .functions import get_video_by_resolution

class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'original_file', 'genre']



class VideoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'thumbnail','upload_date', 'genre']


class VideoDetailSerializer(serializers.ModelSerializer):
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
        return self._get_video_url(obj, '180p')

    def get_video_360p(self, obj):
        return self._get_video_url(obj, '360p')

    def get_video_720p(self, obj):
        return self._get_video_url(obj, '720p')

    def get_video_1080p(self, obj):
        return self._get_video_url(obj, '1080p')

    def get_resolution(self, obj):
        # Default resolution (z.B. 720p)
        return '720p'
 
    def get_video_url(self, obj):
        # Default video URL, z.B. 720p
        request = self.context.get('request')
        video_file = get_video_by_resolution(obj, '720p')
        if video_file and hasattr(video_file, 'url'):
            return request.build_absolute_uri(video_file.url) if request else video_file.url
        return None
    
    def get_last_position(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            progress = VideoProgress.objects.filter(user=user, video=obj).first()
            if progress:
                return progress.position_in_seconds
        return 0

    def _get_video_url(self, obj, resolution):
        request = self.context.get('request')
        video_file = get_video_by_resolution(obj, resolution)
        if video_file and hasattr(video_file, 'url'):
            return request.build_absolute_uri(video_file.url) if request else video_file.url
        return None