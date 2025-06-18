# videoflix/api/urls.py
from django.urls import path
from .views import VideoUploadView, VideoListView, VideoDetailView,VideoProgressUpdateView, VideoStreamView, ContinueWatchingView

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('video/<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
    path('video/progress/', VideoProgressUpdateView.as_view(), name='video-progress'),
    path('video/continue/', ContinueWatchingView.as_view(), name='continue-watching'),
path('stream/<str:pk>/<str:resolution>/<str:filename>/', VideoStreamView.as_view(), name='video-stream'),

]
