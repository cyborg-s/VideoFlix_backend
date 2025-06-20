from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from email.mime.image import MIMEImage


def send_activation_email(user, request):
    """
    Sends an account activation email to the given user containing a link
    with a base64-encoded user ID and a token for account verification.

    Args:
        user (User): The user instance to whom the activation email will be sent.
        request (HttpRequest): The current HTTP request instance (not used in this implementation).

    Process:
        - Generates a URL-safe base64 encoded user ID (uid).
        - Generates an activation token using Django's default_token_generator.
        - Constructs an activation link targeting the frontend domain with uid and token as query parameters.
        - Prepares email subject, sender, and recipient.
        - Renders an HTML email template with context including the user and activation link.
        - Creates a multipart email with plain text and HTML content.
        - Attaches an inline image (logo) to the email using MIMEImage.
        - Sends the email to the user's email address.
    """
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
