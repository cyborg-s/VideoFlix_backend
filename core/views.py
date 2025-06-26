from django.conf import settings
from django.http import JsonResponse

def test_env_view(request):
    return JsonResponse({
        "SECRET_KEY": settings.SECRET_KEY,
        "EMAIL_HOST": settings.EMAIL_HOST,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_USE_TLS": settings.EMAIL_USE_TLS,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
        "DEBUG": settings.DEBUG,
    })