import subprocess
from PIL import Image
from moviepy import VideoFileClip

from ..models import VideoProgress


def convert_video(input_path, output_path, resolution):
    height = resolution
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_path,
    ]

    subprocess.run(command, check=True)


def generate_thumbnail(input_path, output_path):
    clip = VideoFileClip(input_path)
    frame = clip.get_frame(1)
    image = Image.fromarray(frame)
    image.save(output_path)


def get_video_by_resolution(video, resolution: str):
    resolution_map = {
        '180p': video.video_180p,
        '360p': video.video_360p,
        '720p': video.video_720p,
        '1080p': video.video_1080p,
    }
    return resolution_map.get(resolution)


def save_video_progress(user_id, video_id, position_in_seconds):
    obj, created = VideoProgress.objects.update_or_create(
        user_id=user_id,
        video_id=video_id,
        defaults={'position_in_seconds': position_in_seconds}
    )
    return obj


def get_video_progress(user_id, video_id):
    try:
        progress = VideoProgress.objects.get(
            user_id=user_id, video_id=video_id)
        return progress.position_in_seconds
    except VideoProgress.DoesNotExist:
        return 0.0
