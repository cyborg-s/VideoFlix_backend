from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def send_password_reset_email(email, request):
    print("send_password_reset_email wurde aufgerufen")
    if not email:
        logger.warning("Keine E-Mail angegeben.")
        return

    try:
        user = User.objects.get(email__iexact=email)
        if not user.is_active:
            logger.warning("Benutzer nicht aktiv: %s", email)
            return

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        send_mail(
            subject="Passwort zurücksetzen",
            message=(
                f"Hier ist dein Link zum Zurücksetzen des Passworts:\n\n{reset_link}\n\n"
                f"Falls du das nicht angefordert hast, ignoriere diese Mail."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info("Passwort-Zurücksetzungslink an %s gesendet.", email)

    except User.DoesNotExist:
        logger.warning("Kein Benutzer gefunden mit E-Mail: %s", email)
        # absichtlich keine Fehlermeldung zurückgeben (Datenschutz)
        pass
