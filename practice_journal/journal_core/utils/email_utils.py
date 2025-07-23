from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_email_confirmation(user, is_new_user=False):
    """
    Send email confirmation email to user
    """
    token = user.generate_email_confirmation_token()
    frontend_url = settings.FRONTEND_URL
    
    if is_new_user:
        # For new user registration
        confirmation_url = f"{frontend_url}/confirm-email?token={token}"
        subject = "Confirm your Jam Jar account"
        html_message = f"""
        <p>Welcome to Jam Jar!</p>
        <p>Please click <a href="{confirmation_url}">here</a> to confirm your email address and activate your account.</p>
        <p>If you didn't create this account, you can safely ignore this email.</p>
        """
    else:
        # For email address change
        confirmation_url = f"{frontend_url}/confirm-email?token={token}"
        subject = "Confirm your new email address"
        html_message = f"""
        <p>Hello {user.username},</p>
        <p>Please click <a href="{confirmation_url}">here</a> to confirm your new email address.</p>
        <p>If you didn't request this change, please contact support immediately.</p>
        """
    
    try:
        send_mail(
            subject=subject,
            message="",  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email confirmation: {e}")
        return False 