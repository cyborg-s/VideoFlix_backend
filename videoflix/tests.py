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
    return SimpleUploadedFile(
        "test_video.mp4",
        b"fake video content",
        content_type="video/mp4"
    )


def get_temp_image():
    image = Image.new('RGB', (100, 100))
    tmp_file = io.BytesIO()
    image.save(tmp_file, format='JPEG')
    tmp_file.seek(0)
    return SimpleUploadedFile("thumbnail.jpg", tmp_file.read(), content_type="image/jpeg")


class VideoTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

    def test_video_upload(self):
        url = reverse('video-upload')
        data = {
            'title': 'Test Video',
            'description': 'Kurzbeschreibung',
            'original_file': get_temp_video_file(),
            'genre': 'action',
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', response.data)
        self.assertTrue(Video.objects.filter(title='Test Video').exists())

    def test_video_detail_with_progress(self):
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_position'], 45.5)

    def test_video_progress_update(self):
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        progress = VideoProgress.objects.get(user=self.user, video=video)
        self.assertEqual(progress.position_in_seconds, 87.3)

    def test_get_video_by_resolution_returns_correct_field(self):
        video = Video(
            video_180p='path/to/180p.mp4',
            video_360p='path/to/360p.mp4',
            video_720p='path/to/720p.mp4',
            video_1080p='path/to/1080p.mp4',
        )
        self.assertEqual(functions.get_video_by_resolution(
            video, '180p'), 'path/to/180p.mp4')
        self.assertEqual(functions.get_video_by_resolution(
            video, '360p'), 'path/to/360p.mp4')
        self.assertEqual(functions.get_video_by_resolution(
            video, '720p'), 'path/to/720p.mp4')
        self.assertEqual(functions.get_video_by_resolution(
            video, '1080p'), 'path/to/1080p.mp4')
        self.assertIsNone(functions.get_video_by_resolution(video, '240p'))

    def test_save_video_progress_creates_and_updates(self):
        video = Video.objects.create(
            title='Save Progress Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='action'
        )
        obj = functions.save_video_progress(self.user.id, video.id, 12.5)
        self.assertEqual(obj.position_in_seconds, 12.5)

        obj2 = functions.save_video_progress(self.user.id, video.id, 20.0)
        self.assertEqual(obj2.position_in_seconds, 20.0)
        self.assertEqual(obj.id, obj2.id)

    def test_get_video_progress_returns_correct_value_or_zero(self):
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
        self.assertEqual(pos, 30.0)

        video2 = Video.objects.create(
            title='No Progress Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='drama'
        )
        pos2 = functions.get_video_progress(self.user.id, video2.id)
        self.assertEqual(pos2, 0.0)

    def test_video_str_method(self):
        video = Video(title="Mein Video")
        self.assertEqual(str(video), "Mein Video")

    def test_video_progress_str_method(self):
        video = Video.objects.create(
            title='Progress Str Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='comedy'
        )
        vp = VideoProgress.objects.create(
            user=self.user, video=video, position_in_seconds=12.3)
        self.assertIn(str(self.user.username), str(vp))
        self.assertIn(str(video.title), str(vp))

    def test_video_progress_unique_constraint(self):
        video = Video.objects.create(
            title='Unique Constraint Video',
            description='Beschreibung',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='thriller'
        )
        VideoProgress.objects.create(
            user=self.user, video=video, position_in_seconds=10)
        with self.assertRaises(Exception):
            VideoProgress.objects.create(
                user=self.user, video=video, position_in_seconds=20)

    def test_video_upload_invalid_data(self):
        url = reverse('video-upload')
        data = {'title': '', 'description': '',
                'original_file': '', 'genre': ''}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_video_detail_with_no_progress(self):
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('last_position'), 0)

    def test_video_detail_invalid_resolution(self):
        video = Video.objects.create(
            title='Invalid Resolution Video',
            description='desc',
            original_file=get_temp_video_file(),
            thumbnail=get_temp_image(),
            genre='comedy'
        )
        url = reverse('video-detail', kwargs={'pk': video.id})
        response = self.client.get(url, {'resolution': '1080p'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_video_detail_video_not_found(self):
        url = reverse('video-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_video_progress_update_missing_fields(self):
        url = reverse('video-progress')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_video_progress_update_video_not_found(self):
        url = reverse('video-progress')
        data = {'video_id': 9999, 'position_in_seconds': 10}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_video_progress_update_permission_denied(self):
        self.client.force_authenticate(user=None)
        url = reverse('video-progress')
        data = {'video_id': 1, 'position_in_seconds': 50}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
