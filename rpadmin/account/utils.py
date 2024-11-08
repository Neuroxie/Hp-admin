from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .token_generator import account_activation_token  # Updated import

import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

def send_verification_email(user):
    current_site = '85.31.235.12:5000'  # Change to your domain in production
    mail_subject = 'Activate your account'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    activation_link = f"http://{current_site}/account/activate/{uid}/{token}/"
    
    message = f"Hi {user.name},\n\nPlease click on the link below to activate your account:\n{activation_link}\n\nThank you!"
    send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


# def generate_otp(length=6):
#     return ''.join(random.choices(string.digits, k=length))

# def send_otp_email(user, otp):
#     subject = 'Your OTP Code'
#     message = f'Your OTP code is {otp}. It will expire in 10 minutes.'
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

# def is_otp_valid(user, otp):
#     if user.otp == otp and timezone.now() < user.otp_expiration:
#         return True
#     return False