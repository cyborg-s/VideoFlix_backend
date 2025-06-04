from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django_rq import enqueue

from .serializers import VideoUploadSerializer, VideoListSerializer, VideoDetailSerializer
from ..models import Video
from .tasks import process_video
from .functions import get_video_by_resolution, save_video_progress, get_video_progress


class VideoUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = VideoUploadSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save()
            process_video.delay(video.id)
            return Response({"detail": "Video hochgeladen. Verarbeitung läuft im Hintergrund."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoListView(APIView):
    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)


class VideoDetailView(APIView):
    def get(self, request, pk):
        resolution = request.query_params.get('resolution', '720p')
        user_id = request.query_params.get('user_id')

        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

        selected_video_file = get_video_by_resolution(video, resolution)

        if not selected_video_file:
            return Response({'error': f'{resolution} version not available'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = VideoDetailSerializer(video, context={'request': request})
        data = serializer.data
        data['video_url'] = request.build_absolute_uri(selected_video_file.url)
        data['resolution'] = resolution
        if user_id:
            data['last_position'] = get_video_progress(user_id, pk)

        return Response(data)






class VideoProgressUpdateView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        video_id = request.data.get('video_id')
        position = request.data.get('position_in_seconds')

        if not all([user_id, video_id, position]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        save_video_progress(user_id, video_id, position)
        return Response({'detail': 'Progress saved.'}, status=status.HTTP_200_OK)
