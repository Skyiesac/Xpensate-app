
from django.core.mail import send_mail
from django.conf import settings
from xpensateapp.settings import EMAIL_HOST_USER
                
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
     print(90)
     try:
        print(2)
        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully.")
     except Exception as e:
        print(f"Error sending email: {e}") 