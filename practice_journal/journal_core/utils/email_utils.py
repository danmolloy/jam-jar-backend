from django.conf import settings
from django.template.loader import render_to_string
from .ses import send_html_email

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
        # Create plain text version from HTML
        plain_text = f"Please visit {confirmation_url} to confirm your email address."
        
        return send_html_email(
            subject=subject,
            html_content=html_message,
            to_email=user.email,
            text_content=plain_text,
        )
    except Exception as e:
        print(f"Error sending email confirmation: {e}")
        return False 