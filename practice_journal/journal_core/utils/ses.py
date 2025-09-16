import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Create SES client
ses_client = boto3.client(
    'ses',
    region_name=settings.AWS_S3_REGION_NAME,  # Reuse existing AWS region setting
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def send_email(subject, message, to_email, from_email=None, html_message=None):
    """
    Send email using AWS SES
    
    Args:
        subject (str): Email subject
        message (str): Plain text email content
        to_email (str): Recipient email address
        from_email (str, optional): Sender email address. Defaults to DEFAULT_FROM_EMAIL
        html_message (str, optional): HTML email content
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        # Prepare email parameters
        email_params = {
            'Source': from_email,
            'Destination': {
                'ToAddresses': [to_email]
            },
            'Message': {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': message,
                        'Charset': 'UTF-8'
                    }
                }
            }
        }
        
        # Add HTML content if provided
        if html_message:
            email_params['Message']['Body']['Html'] = {
                'Data': html_message,
                'Charset': 'UTF-8'
            }
        
        # Send email
        response = ses_client.send_email(**email_params)
        logger.info(f"Email sent successfully to {to_email}. MessageId: {response['MessageId']}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Failed to send email to {to_email}. Error: {error_code} - {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to_email}: {e}")
        return False

def send_html_email(subject, html_content, to_email, from_email=None, text_content=None):
    """
    Send HTML email using AWS SES
    
    Args:
        subject (str): Email subject
        html_content (str): HTML email content
        to_email (str): Recipient email address
        from_email (str, optional): Sender email address. Defaults to DEFAULT_FROM_EMAIL
        text_content (str, optional): Plain text fallback content
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        # Prepare email parameters
        email_params = {
            'Source': from_email,
            'Destination': {
                'ToAddresses': [to_email]
            },
            'Message': {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': html_content,
                        'Charset': 'UTF-8'
                    }
                }
            }
        }
        
        # Add text content if provided
        if text_content:
            email_params['Message']['Body']['Text'] = {
                'Data': text_content,
                'Charset': 'UTF-8'
            }
        
        # Send email
        response = ses_client.send_email(**email_params)
        logger.info(f"HTML email sent successfully to {to_email}. MessageId: {response['MessageId']}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Failed to send HTML email to {to_email}. Error: {error_code} - {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending HTML email to {to_email}: {e}")
        return False
