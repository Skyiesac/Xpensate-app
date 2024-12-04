
from django.core.mail import send_mail
import re
from django.conf import settings
from xpensateapp.settings import EMAIL_HOST_USER
import random
import requests
from decouple import config
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

def logout_all_sessions(self, user):
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            # Blacklist the token
            _, _ = BlacklistedToken.objects.get_or_create(token=token)    
            
def normalize_email(email):
        
        email = email or ''
        try:
            email_name, domain_part = email.lower().strip().rsplit('@', 1)
        except ValueError:
            return email
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email
    

def otp_for_reset(email,otp):
     subject="OTP to Reset Password "
     message = f"""
Your OTP to reset your password for Xpensate app is:
{otp}
This OTP is valid only for 5 minutes.
Do not share your otp with anyone.
-Xpensate
"""
     
     from_email = settings.EMAIL_HOST_USER
     recipient_list = [email]

     return send_mail(subject, message, from_email , recipient_list)


def send_verify_mail(email , otp):
     subject="Verifying your Registeration"
     message= f"""
Hello,
This mail is sent to you by team Xpensate for confirming your registeration on the application.
OTP for verification is-
OTP = {otp}.
This OTP is valid for only 5 minutes.
Do not share your otp with anyone.
-Xpensate
"""
     from_email = settings.EMAIL_HOST_USER
     recipient_list = [email]
     try:
        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully.")
     except Exception as e:
        print(f"Error sending email: {e}") 

def strong_pass(password):
        if (len(password) < 8 or 
            (not re.findall('\d', password)) or 
            (not re.findall('[A-Z]', password)) or 
            (not re.findall('[a-z]', password))or 
            (not re.findall('[!@#$%&*]', password))):
            return False
        else:
            return True
        
def send_otpphone(contact):
    otp = random.randint(1000, 9999)
    api_key= config('PHONE_API')
    url=f"https://2factor.in/API/V1/{api_key}/SMS/{contact}/{otp}"
    response = requests.get(url)
    return otp
   
# def logout_all_sessions(self, user):
#         user.auth_token_set.all().delete()
