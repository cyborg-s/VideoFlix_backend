from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import VideoUploadSerializer, VideoListSerializer, VideoDetailSerializer
from ..models import Video, VideoProgress
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
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        resolution = request.query_params.get('resolution', '720p')

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

        # Hole Fortschritt für den authentifizierten Benutzer
        if request.user.is_authenticated:
            progress = VideoProgress.objects.filter(user=request.user, video=video).first()
            data['last_position'] = progress.position_in_seconds if progress else 0

        return Response(data)





class VideoProgressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        video_id = request.data.get('video_id')
        position = request.data.get('position_in_seconds')

        if not all([video_id, position]):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Fortschritt speichern oder aktualisieren
        VideoProgress.objects.update_or_create(
            user=request.user,
            video=video,
            defaults={'position_in_seconds': position}
        )

        return Response({'detail': 'Progress saved.'}, status=status.HTTP_200_OK)
