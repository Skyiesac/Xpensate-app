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


def email_for_joining(email, name):
     subject=f"Welcome to {name}"
     message = f"""
Hello user,

Welcome to your new Xpensate group "{name}" !

You're now part of a community where you can easily track and manage your shared expenses.

Here's what you can do:

Add Expenses: Easily log your expenses, big or small.
Track Spending: Keep a detailed record of your contributions.
Settle Up Easily: Let Xpensate calculate who owes who.
Stay Organized: Manage your group's finances effortlessly.
Let's make group expenses a breeze!

By-
The Xpensate team
"""
     
     from_email = settings.EMAIL_HOST_USER
     recipient_list = [email]

     return send_mail(subject, message, from_email , recipient_list)

def invite_email(email,invitecode, name):
     subject=f"Welcome to {name}"
     message = f"""
Hello user,
This is an invite mail sent to you for joing {name} group on Xpensate. 
invite code is -{invitecode}
Fill this code on the app to join this cool group !

By-
The Xpensate team
"""
     
     from_email = settings.EMAIL_HOST_USER
     recipient_list = [email]

     return send_mail(subject, message, from_email , recipient_list)

def email_for_paying(email,member, amount, why):
     subject=f"{amount} credited into your account"
     message = f"""
Hello user,
This is to inform you that {member} user has paid you the amount of {amount}  INR. 
(PS: This transaction is only virtual as for now , not appropriate for any legal purposes)

By-
The Xpensate team
"""
     
     from_email = settings.EMAIL_HOST_USER
     recipient_list = [email]

     return send_mail(subject, message, from_email , recipient_list)