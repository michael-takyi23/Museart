from django.core.mail import send_mail
from django.conf import settings

def send_custom_email(subject, message, recipient_list):
    """
    Utility function to send emails using the configured email backend.
    
    Args:
        subject (str): Email subject.
        message (str): Email body content.
        recipient_list (list): List of recipient email addresses.

    Returns:
        bool: True if email is sent successfully, False otherwise.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
