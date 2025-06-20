import subprocess
from PIL import Image
from moviepy import VideoFileClip

from ..models import VideoProgress


def convert_video(input_path: str, output_path: str, resolution: int) -> None:
    """
    Convert a video to a specified vertical resolution using ffmpeg.

    Args:
        input_path (str): Path to the source video file.
        output_path (str): Path where the converted video will be saved.
        resolution (int): Target height in pixels for the output video.
    """
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


def generate_thumbnail(input_path: str, output_path: str) -> None:
    """
    Generate a thumbnail image from the first second of a video.

    Args:
        input_path (str): Path to the video file.
        output_path (str): Path where the thumbnail image will be saved.
    """
    clip = VideoFileClip(input_path)
    frame = clip.get_frame(1)
    image = Image.fromarray(frame)
    image.save(output_path)


def get_video_by_resolution(video, resolution: str):
    """
    Retrieve the video file field corresponding to the given resolution.

    Args:
        video: Video model instance containing different resolution fields.
        resolution (str): Resolution key ('180p', '360p', '720p', '1080p').

    Returns:
        The video file corresponding to the resolution or None if not found.
    """
    resolution_map = {
        '180p': video.video_180p,
        '360p': video.video_360p,
        '720p': video.video_720p,
        '1080p': video.video_1080p,
    }
    return resolution_map.get(resolution)


def save_video_progress(user_id: int, video_id: int, position_in_seconds: float):
    """
    Save or update the video watching progress for a user.

    Args:
        user_id (int): ID of the user.
        video_id (int): ID of the video.
        position_in_seconds (float): Current playback position in seconds.

    Returns:
        VideoProgress instance that was created or updated.
    """
    obj, created = VideoProgress.objects.update_or_create(
        user_id=user_id,
        video_id=video_id,
        defaults={'position_in_seconds': position_in_seconds}
    )
    return obj


def get_video_progress(user_id: int, video_id: int) -> float:
    """
    Retrieve the saved video progress position for a user and video.

    Args:
        user_id (int): ID of the user.
        video_id (int): ID of the video.

    Returns:
        float: The saved playback position in seconds, or 0.0 if no progress found.
    """
    try:
        progress = VideoProgress.objects.get(
            user_id=user_id, video_id=video_id)
        return progress.position_in_seconds
    except VideoProgress.DoesNotExist:
        return 0.0
