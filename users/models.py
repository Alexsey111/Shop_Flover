from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    telegram_username = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    chat_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'




# class CustomUser(AbstractUser):
#     telegram_username = models.CharField(max_length=255, blank=True, null=True)
#     phone = models.CharField(max_length=15, blank=True, null=True)  # Добавляем поле phone
#     address = models.TextField(blank=True, null=True)  # Добавляем поле address
#     chat_id = models.CharField(max_length=100, null=True, blank=True)
#
#     class Meta:
#         verbose_name = 'Custom User'
#         verbose_name_plural = 'Custom Users'

