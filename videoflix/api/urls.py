# videoflix/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_list, name='video-list'),  # z. B. /video/
    path('<int:id>/', views.video_detail, name='video-detail'),  # z. B. /video/3/
]