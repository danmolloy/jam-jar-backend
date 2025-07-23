from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.conf import settings

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    frontend_url = settings.FRONTEND_URL
    reset_link = f"{frontend_url}/reset-password?token={reset_password_token.key}"

    html = f"""
    <p>Hello,</p>
    <p>Click <a href="{reset_link}">here</a> to reset your password.</p>
    <p>If you didn't request this, just ignore this email.</p>
    """

    send_mail(
        subject="Reset your Jam Jar password",
        message="",  # Optional plain text fallback
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reset_password_token.user.email],
        html_message=html
    ) 