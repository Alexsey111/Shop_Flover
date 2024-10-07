from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    chat_id = models.BigIntegerField(blank=True, null=True)


    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'



