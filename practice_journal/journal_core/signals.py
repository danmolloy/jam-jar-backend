from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings
from .utils.ses import send_html_email

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    frontend_url = settings.FRONTEND_URL
    reset_link = f"{frontend_url}/reset-password?token={reset_password_token.key}"

    html = f"""
    <p>Hello,</p>
    <p>Click <a href="{reset_link}">here</a> to reset your password.</p>
    <p>If you didn't request this, just ignore this email.</p>
    """

    # Create plain text version
    plain_text = f"Click here to reset your password: {reset_link}"
    
    send_html_email(
        subject="Reset your Jam Jar password",
        html_content=html,
        to_email=reset_password_token.user.email,
        text_content=plain_text,
    ) 