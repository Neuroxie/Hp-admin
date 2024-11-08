import random
import string
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
from datahub.models import District
from phonenumber_field.modelfields import PhoneNumberField
from datahub.models import Thana


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('normal', 'Normal User'),
        ('police', 'Police User'),
    ]
    
    email = models.EmailField(unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='pp/', blank=True, null=True)
    name = models.CharField(max_length=255)
    phone = PhoneNumberField(unique=True, null=True, blank=True)
    lat = models.CharField(max_length=255, null=True, blank=True)
    lon = models.CharField(max_length=255, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    dob = models.DateField(null=True, blank=True)  # Only for Police Users
    thana = models.CharField(max_length=100, blank=True, null=True)
    batch = models.CharField(max_length=100, null=True, blank=True)
    bp = models.CharField(max_length=100, null=True, blank=True)
    rank = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=1000, blank=True, null=True)
    nid = models.CharField(max_length=20, null=True, blank=True)
    profession = models.CharField(max_length=50, null=True, blank=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_on_duty = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return str(self.phone)

    def generate_otp(self):
        otp = ''.join(random.choices(string.digits, k=6))
        self.otp = otp
        self.otp_expires_at = timezone.now() + timezone.timedelta(minutes=10)
        self.save()
        return otp

    class Meta:
        permissions = [
            ('can_view_police_users', 'Can view police users'),
        ]
    
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True
    )

class Logs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='logs')
    police = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='police_logs')
    time = models.DateTimeField(default=timezone.now)
    
    # User's location
    user_lat = models.CharField(max_length=255)
    user_lon = models.CharField(max_length=255)
    
    # Police's location
    police_lat = models.CharField(max_length=255, null=True, blank=True)
    police_lon = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, default='Unassigned')

    def __str__(self):
        return f"Log: {self.user.phone} -> {self.police.phone} at {self.time}"