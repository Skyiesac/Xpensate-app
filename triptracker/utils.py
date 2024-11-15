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
