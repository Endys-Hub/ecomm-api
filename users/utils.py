from django.core.mail import send_mail
from django.conf import settings

def sendMail(email):
    subject = "Welcome to the Ultra Application"
    message = f'''
                    This is an onboarding email welcoming you to Ultra!!!
                    Have a pleasant stay with us as we guide you through.
            '''
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER, #sender email
        [email], #recipient
        fail_silently=False,
    )