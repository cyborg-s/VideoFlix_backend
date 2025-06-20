import io
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image

from videoflix.models import Video, VideoProgress
from videoflix.api import functions

User = get_user_model()


def get_temp_video_file():
    """
    Create and return a temporary uploaded video file for testing.
    
    Returns:
        SimpleUploadedFile: An in-memory video file with dummy content.
    """
    return SimpleUploadedFile(
        "test_video.mp4",
        b"fake video content",
        content_type="video/mp4"
    )


def get_temp_image():
    """
    Create and return a temporary uploaded image file for testing.
    
    Returns:
        SimpleUploadedFile: An in-memory JPEG image file.
    """
    image = Image.new('RGB', (100, 100))
    tmp_file = io.BytesIO()
    image.save(tmp_file, format='JPEG')
    tmp_file.seek(0)
    return SimpleUploadedFile("thumbnail.jpg", tmp_file.read(), content_type="image/jpeg")


class VideoTestCase(TestCase):
    """
    TestCase class for testing video-related API endpoints and utility functions.
    """
    def setUp(self):
        """
        Setup test environment including test user and authenticated API client.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_video_upload(self):
        """
        Test uploading a video via the API and verify successful creation.
        """
        url = reverse('video-upload')
        data = {
            'title': 'Test Video',
            'description': 'Kurzbeschreibung',
            'original_file': get_temp_video_file(),
            'genre': 'action',
        }
        response = self.client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'detail' in response.data
        assert Video.objects.filter(title='Test Video').exists()

    def test_video_detail_with_progress(self):
        """
        Test retrieving video details including the user's last watched position.
        """
        video = Video.objects.create(
            title='Testvideo',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            video_180p=get_temp_video_file(),
            video_360p=get_temp_video_file(),
            video_720p=get_temp_video_file(),
            video_1080p=get_temp_video_file(),
            genre='comedy'
        )
        VideoProgress.objects.create(
            user=self.user, video=video, position_in_seconds=45.5)

        url = reverse('video-detail', kwargs={'pk': video.id})
        response = self.client.get(url, {'resolution': '720p'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['last_position'] == 45.5

    def test_video_progress_update(self):
        """
        Test updating the video progress via the API and verify correct saving.
        """
        video = Video.objects.create(
            title='Fortschritt Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='drama'
        )

        url = reverse('video-progress')
        data = {
            'video_id': video.id,
            'position_in_seconds': 87.3
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

        progress = VideoProgress.objects.get(user=self.user, video=video)
        assert progress.position_in_seconds == 87.3

    def test_get_video_by_resolution_returns_correct_field(self):
        """
        Test that the function get_video_by_resolution returns the correct video file path
        for each supported resolution and None for unsupported resolutions.
        """
        video = Video(
            video_180p='path/to/180p.mp4',
            video_360p='path/to/360p.mp4',
            video_720p='path/to/720p.mp4',
            video_1080p='path/to/1080p.mp4',
        )
        assert functions.get_video_by_resolution(video, '180p') == 'path/to/180p.mp4'
        assert functions.get_video_by_resolution(video, '360p') == 'path/to/360p.mp4'
        assert functions.get_video_by_resolution(video, '720p') == 'path/to/720p.mp4'
        assert functions.get_video_by_resolution(video, '1080p') == 'path/to/1080p.mp4'
        assert functions.get_video_by_resolution(video, '240p') is None

    def test_save_video_progress_creates_and_updates(self):
        """
        Test that save_video_progress creates a new progress record or updates
        an existing one correctly.
        """
        video = Video.objects.create(
            title='Save Progress Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='action'
        )
        obj = functions.save_video_progress(self.user.id, video.id, 12.5)
        assert obj.position_in_seconds == 12.5

        obj2 = functions.save_video_progress(self.user.id, video.id, 20.0)
        assert obj2.position_in_seconds == 20.0
        assert obj.id == obj2.id

    def test_get_video_progress_returns_correct_value_or_zero(self):
        """
        Test that get_video_progress returns the correct progress value if it exists,
        or zero if no progress record exists for the user and video.
        """
        video = Video.objects.create(
            title='Progress Check Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='comedy'
        )
        VideoProgress.objects.create(
            user=self.user, video=video, position_in_seconds=30.0)

        pos = functions.get_video_progress(self.user.id, video.id)
        assert pos == 30.0

        video2 = Video.objects.create(
            title='No Progress Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='drama'
        )
        pos2 = functions.get_video_progress(self.user.id, video2.id)
        assert pos2 == 0.0

    def test_video_str_method(self):
        """
        Test the __str__ method of the Video model returns the title.
        """
        video = Video(title="Mein Video")
        assert str(video) == "Mein Video"

    def test_video_progress_str_method(self):
        """
        Test the __str__ method of the VideoProgress model includes username and video title.
        """
        video = Video.objects.create(
            title='Progress Str Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='comedy'
        )
        vp = VideoProgress.objects.create(
            user=self.user, video=video, position_in_seconds=12.3)
        assert str(self.user.username) in str(vp)
        assert str(video.title) in str(vp)

    def test_video_progress_unique_constraint(self):
        """
        Test that the unique constraint on (user, video) in VideoProgress model
        prevents creating duplicate progress entries for the same user and video.
        """
        video = Video.objects.create(
            title='Unique Constraint Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='thriller'
        )
        VideoProgress.objects.create(
            user=self.user, video=video, position_in_seconds=10)
        try:
            VideoProgress.objects.create(
                user=self.user, video=video, position_in_seconds=20)
            assert False, "Expected exception due to unique constraint"
        except Exception:
            pass

    def test_video_upload_invalid_data(self):
        """
        Test uploading a video with invalid data returns HTTP 400 Bad Request.
        """
        url = reverse('video-upload')
        data = {'title': '', 'description': '',
                'original_file': '', 'genre': ''}
        response = self.client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_video_detail_with_no_progress(self):
        """
        Test retrieving video details when no progress exists returns last_position as 0.
        """
        video = Video.objects.create(
            title='NoProgress Video',
            description='desc',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            video_180p=get_temp_video_file(),
            genre='comedy'
        )
        url = reverse('video-detail', kwargs={'pk': video.id})
        response = self.client.get(url, {'resolution': '180p'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('last_position') == 0

    def test_video_detail_invalid_resolution(self):
        """
        Test retrieving video details with an invalid resolution returns HTTP 400 Bad Request.
        """
        video = Video.objects.create(
            title='Invalid Resolution Video',
            description='desc',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='comedy'
        )
        url = reverse('video-detail', kwargs={'pk': video.id})
        response = self.client.get(url, {'resolution': '1080p'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_video_detail_video_not_found(self):
        """
        Test retrieving video details for a non-existing video returns HTTP 404 Not Found.
        """
        url = reverse('video-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_video_progress_update_missing_fields(self):
        """
        Test updating video progress without required fields returns HTTP 400 Bad Request.
        """
        url = reverse('video-progress')
        response = self.client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_video_progress_update_video_not_found(self):
        """
        Test updating video progress for a non-existing video returns HTTP 404 Not Found.
        """
        url = reverse('video-progress')
        data = {'video_id': 9999, 'position_in_seconds': 10}
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_video_progress_update_permission_denied(self):
        """
        Test updating video progress without authentication returns HTTP 403 Forbidden.
        """
        self.client.force_authenticate(user=None)
        url = reverse('video-progress')
        data = {'video_id': 1, 'position_in_seconds': 50}
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
