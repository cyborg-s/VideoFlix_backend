import os
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError
from django.http import StreamingHttpResponse, HttpResponse, Http404
from wsgiref.util import FileWrapper

from .serializers import VideoUploadSerializer, VideoListSerializer, VideoDetailSerializer
from ..models import Video, VideoProgress
from .tasks import process_video
from .functions import get_video_by_resolution


class VideoUploadView(APIView):
    """
    API endpoint to upload videos.
    Accepts multipart/form-data for video upload.
    Triggers asynchronous processing after saving.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = VideoUploadSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save()
            process_video.delay(video.id)
            return Response(
                {"detail": "Video hochgeladen. Verarbeitung läuft im Hintergrund."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoListView(APIView):
    """
    API endpoint to list all videos.
    Returns serialized list with basic info.
    """

    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoListSerializer(videos, many=True, context={"request": request})
        return Response(serializer.data)


class VideoDetailView(APIView):
    """
    API endpoint to retrieve video details.
    Supports optional resolution query parameter to get specific video URL.
    Includes last watched position for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)

        requested_resolution = request.query_params.get("resolution")
        resolutions = ["180p", "360p", "720p", "1080p"]
        video_urls = {}

        for res in resolutions:
            video_file = get_video_by_resolution(video, res)
            if video_file and hasattr(video_file, "url"):
                filename = os.path.basename(video_file.name)
                video_urls[f"video_{res}"] = request.build_absolute_uri(
                    f"/api/video/stream/{video.id}/{res}/{filename}/"
                )

        if requested_resolution:
            key = f"video_{requested_resolution}"
            if key not in video_urls:
                raise ValidationError(
                    {"resolution": f"Die Auflösung {requested_resolution} ist nicht verfügbar."}
                )
            data = {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "thumbnail": request.build_absolute_uri(video.thumbnail.url) if video.thumbnail else None,
                "genre": video.genre,
                key: video_urls[key],
                "video_url": video_urls[key],
                "resolution": requested_resolution,
            }
        else:
            if not video_urls:
                raise NotFound("Keine verfügbare Videoauflösung gefunden.")

            default_resolution_key = "video_720p" if "video_720p" in video_urls else next(iter(video_urls))
            serializer = VideoDetailSerializer(video, context={"request": request})
            data = serializer.data
            data.update(video_urls)
            data["video_url"] = video_urls[default_resolution_key]
            data["resolution"] = default_resolution_key.replace("video_", "")

        if request.user.is_authenticated:
            progress = VideoProgress.objects.filter(user=request.user, video=video).first()
            data["last_position"] = progress.position_in_seconds if progress else 0

        return Response(data)


class VideoProgressUpdateView(APIView):
    """
    API endpoint to update the playback progress of a video for an authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        video_id = request.data.get("video_id")
        position = request.data.get("position_in_seconds")

        if video_id is None or position is None:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({"error": "Video not found."}, status=status.HTTP_404_NOT_FOUND)

        VideoProgress.objects.update_or_create(
            user=request.user, video=video, defaults={"position_in_seconds": position}
        )

        return Response({"detail": "Progress saved."}, status=status.HTTP_200_OK)


class VideoStreamView(APIView):
    """
    API endpoint to stream video files supporting HTTP Range requests.
    Allows streaming partial content for efficient playback.
    """

    permission_classes = [AllowAny]

    def get(self, request, pk, resolution, filename):
        try:
            video = Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            raise Http404("Video not found")

        video_file = get_video_by_resolution(video, resolution)
        if not video_file or not os.path.exists(video_file.path):
            return HttpResponse("Requested resolution not available.", status=404)

        file_path = video_file.path
        file_size = os.path.getsize(file_path)
        content_type = "video/mp4"

        range_header = request.headers.get("Range", "").strip()
        if not range_header:
            response = StreamingHttpResponse(FileWrapper(open(file_path, "rb")), content_type=content_type)
            response["Content-Length"] = str(file_size)
            return response

        try:
            range_type, range_spec = range_header.split("=")
            range_start, range_end = range_spec.split("-")
            range_start = int(range_start)
            range_end = int(range_end) if range_end else file_size - 1
        except Exception:
            return HttpResponse("Invalid Range Header", status=400)

        length = range_end - range_start + 1
        with open(file_path, "rb") as f:
            f.seek(range_start)
            data = f.read(length)

        response = HttpResponse(data, status=206, content_type=content_type)
        response["Content-Range"] = f"bytes {range_start}-{range_end}/{file_size}"
        response["Accept-Ranges"] = "bytes"
        response["Content-Length"] = str(length)

        return response


class ContinueWatchingView(APIView):
    """
    API endpoint to fetch videos the authenticated user has partially watched.
    Returns a list of videos with current playback positions greater than zero.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        progresses = VideoProgress.objects.filter(user=request.user).select_related("video")
        videos = [
            {
                "id": p.video.id,
                "title": p.video.title,
                "img": request.build_absolute_uri(p.video.thumbnail.url),
                "description": p.video.description,
                "position_in_seconds": p.position_in_seconds,
            }
            for p in progresses
            if p.position_in_seconds > 0
        ]
        return Response(videos)
