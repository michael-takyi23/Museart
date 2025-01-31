from django.core.mail import send_mail
from django.conf import settings


def calculate_cart_total(cart):
    total = 0
    for item_id, item in cart.items():
        if isinstance(item, dict) and 'items_by_size' in item:
            for size, quantity in item['items_by_size'].items():
                total += quantity * item['price']  # Make sure `price` is available
        else:
            total += item * item['price']  # Assuming non-size items are simple integers
    return total


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
