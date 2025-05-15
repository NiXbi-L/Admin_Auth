from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser
    Add any custom fields here as needed
    """
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class EmailVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return timezone.now() <= self.expires_at
