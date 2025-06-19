from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from email.mime.image import MIMEImage


def send_activation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    frontend_domain = "http://localhost:4200"
    activation_link = f"{frontend_domain}/login?uidb64={uid}&token={token}"

    subject = "Aktiviere dein VideoFlix-Konto"
    from_email = "noreply@videoflix.com"
    to = [user.email]

    context = {
        "user": user,
        "activation_link": activation_link,
        "username_clean": user.username.split("_")[0],
    }

    text_content = f"Bitte klicke auf den folgenden Link zur Aktivierung:\n\n{activation_link}"
    html_content = render_to_string("emails/activation_email.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")

    with open('./registration/templates/emails/Capa_1.png', 'rb') as f:
        logo = MIMEImage(f.read())
        logo.add_header('Content-ID', '<logo_image>')
        msg.attach(logo)

    msg.send()
