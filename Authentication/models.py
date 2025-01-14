from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.core.validators import MinLengthValidator
from django.utils import timezone
from celery import shared_task
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.authentication import JWTAuthentication
from storages.backends.s3boto3 import S3Boto3Storage


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):

        if not email:
            raise ValueError("Users must have an email address")

        if not password:
            raise ValueError("Users must have a Password")

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
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    contact = models.CharField(max_length=16, null=True, blank=True)
    currency_rate = models.DecimalField(default=1, max_digits=10, decimal_places=6)
    monthlylimit = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profile_image = models.FileField(null=True, blank=True, upload_to="profile_pics/")

    objects = UserManager()

    USERNAME_FIELD = "email"
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

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        refresh["email"] = self.email
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class EmailOTP(models.Model):

    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)

    otp = models.IntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    forgot = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.email}"


class Register_user(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    password = models.CharField(
        null=True, validators=[MinLengthValidator(8, "Password must have 8 letters")]
    )
    confirm_password = models.CharField(
        max_length=50,
        null=True,
        validators=[MinLengthValidator(8, "Password must have 8 letters")],
    )
    otp = models.IntegerField(blank=True, null=True)


class PhoneOTP(models.Model):
    contact = models.CharField(max_length=10, unique=True)
    otp = models.IntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.contact}"


class FCMToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fcm_token = models.TextField()

    def __str__(self):
        return f"{self.user.email}"


# unique title for each
# dummy data nd postman
# currency rate
