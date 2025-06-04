from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

def send_activation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    domain = get_current_site(request).domain
    activation_link = f"http://{domain}" + reverse("activate", kwargs={"uidb64": uid, "token": token})

    send_mail(
        subject="Activate your account",
        message=f"Click to activate your account:\n\n{activation_link}",
        from_email="noreply@videoflix.com",
        recipient_list=[user.email],
        fail_silently=False,
    )