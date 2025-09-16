from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .ses import send_email
from django.contrib.auth.tokens import PasswordResetTokenGenerator

FRONTEND_URL = settings.FRONTEND_URL

password_reset_token = PasswordResetTokenGenerator()

def send_email_confirmation(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    confirmation_url = f"{FRONTEND_URL}/confirm-email/{uid}/{token}"

    send_email(
        subject="Confirm your email",
        message=f"Click the link to confirm your email: {confirmation_url}",
        to_email=user.email,
    )