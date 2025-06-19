import os
from django.conf import settings
from videoflix.models import Video
from django_rq import job

from .functions import convert_video, generate_thumbnail

@job
def process_video(video_id):
    video = Video.objects.get(id=video_id)
    input_path = video.original_file.path
    base_filename = os.path.splitext(os.path.basename(input_path))[0]
    media_root = settings.MEDIA_ROOT

    resolutions = [180, 360, 720, 1080]
    for res in resolutions:
        output_path = os.path.join(
            media_root, f'videos/{res}p/{base_filename}_{res}p.mp4')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        convert_video(input_path, output_path, res)
        setattr(video, f'video_{res}p',
                f'videos/{res}p/{base_filename}_{res}p.mp4')

    thumbnail_path = os.path.join(
        media_root, f'videos/thumbnails/{base_filename}.jpg')
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
    generate_thumbnail(input_path, thumbnail_path)
    video.thumbnail = f'videos/thumbnails/{base_filename}.jpg'

    video.save()
