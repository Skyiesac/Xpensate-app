from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import MinLengthValidator
from django.utils import timezone
from celery import shared_task 

class UserManager(BaseUserManager):
    def create_user(self, email,password=None):
        
        if not email:
            raise ValueError('Users must have an email address')
        
        if not password:
            raise ValueError('Users must have a Password')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
    
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
    @property
    def is_Active(self):
        return self.is_active
    
    @property
    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        refresh['email'] = self.email
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
   
class EmailOTP(models.Model):
    
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True )
    
    otp = models.IntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    forgot=models.BooleanField(default= False, blank= True)
    def __str__(self):
        return f"{self.email}"
    def delete_after5(self):
        delete_otp_users.apply_async((self.email,), countdown=300)
   
    
class Register_user(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=50,null=True, validators=[MinLengthValidator(8,'Password must have 8 letters')])
    confirm_password = models.CharField(max_length=50,null=True,validators=[MinLengthValidator(8,'Password must have 8 letters')])
    otp = models.IntegerField(blank=True, null=True)
    
    def delete_after10(self):
        delete_registeruser.apply_async((self.email,), countdown=600)

@shared_task
def delete_otp_users(email):
    try:
        instance= EmailOTP.objects.get(email=email)
        instance.delete()
        print("deleted")
    except:
        print("doesn't exist")

@shared_task
def delete_registeruser(email):
    try:
        instance = Register_user.objects.get(email=email)
        instance.delete()
        print("deleted")
    except:
        print("doesn't exist")
