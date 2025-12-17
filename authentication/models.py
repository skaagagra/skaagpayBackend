from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, password=None):
        if not phone_number:
            raise ValueError('Users must have a phone number')
        
        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password=None):
        user = self.create_user(
            phone_number=phone_number,
            full_name=full_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    custom_user_id = models.CharField(max_length=50, unique=True, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    def save(self, *args, **kwargs):
        if not self.custom_user_id and self.phone_number:
            self.custom_user_id = f"{self.phone_number}@skaag"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number
