import os
import random
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code(length=6):
    """Generate a random verification code"""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(user_email, verification_code):
    """Send verification email with code"""
    subject = 'Your Email Verification Code'
    message = f'Your verification code is: {verification_code}\nThis code will expire in 30 minutes.'

    # Get email settings from environment variables
    from_email = os.environ.get('EMAIL_HOST_USER')

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
