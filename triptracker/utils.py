import random
import string
from django.core.mail import send_mail
import re
from django.conf import settings
from xpensateapp.settings import EMAIL_HOST_USER

def generate_invite_code(length=8):
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choices(characters, k=length))
    return code


def email_for_joining(email,otp):
     subject=""
     message = f"""
Hello user, 
You have been added to the trip tracking group.
-Xpensate
"""
     
     from_email = settings.EMAIL_HOST_USER
     recipient_list = [email]

     return send_mail(subject, message, from_email , recipient_list)
