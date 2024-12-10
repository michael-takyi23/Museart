from django.shortcuts import render
from home.utils import send_custom_email


# Index View
def index(request):
    """ A view to return the index page """
    return render(request, 'home/index.html')


# Welcome Email View
def some_view(request):
    """ Example view to send a welcome email """
    if request.method == "POST":
        # Email details
        subject = "Welcome to Museart!"
        message = "Thank you for signing up for Museart. We hope you enjoy your experience!"
        recipient_list = ["museart2024@outlook.com"]

        # Send email
        if send_custom_email(subject, message, recipient_list):
            print("Email sent successfully.")
        else:
            print("Failed to send email.")
    return render(request, "some_template.html")


# Contact Form Email View
def contact_view(request):
    """ A view to handle contact form submissions """
    if request.method == "POST":
        # Collect form data
        name = request.POST.get("name", "Anonymous")
        email = request.POST.get("email", "No Email Provided")
        message = request.POST.get("message", "No Message Provided")

        # Prepare email content
        subject = f"Contact Form Submission from {name}"
        email_message = f"Message from {name} ({email}):\n\n{message}"
        recipient_list = ["museart2024@outlook.com"]  # Admin or support email

        # Send email
        if send_custom_email(subject, email_message, recipient_list):
            success_message = "Your message was sent successfully!"
        else:
            success_message = "Failed to send your message. Please try again."

        # Render confirmation page
        return render(request, "contact_confirmation.html", {"message": success_message})

    return render(request, "contact_form.html")
