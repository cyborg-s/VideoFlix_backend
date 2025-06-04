from django.urls import path
from .views import PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('request-password-reset/', PasswordResetRequestView.as_view(), name='request-password-reset'),
    path('confirm-password-reset/', PasswordResetConfirmView.as_view(), name='confirm-password-reset'),
]