from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomSignupForm(UserCreationForm):
    username = forms.CharField(max_length=30, label='Имя на сайте')
    first_name = forms.CharField(max_length=30, label='Имя')
    last_name = forms.CharField(max_length=30, label='Фамилия')
    phone = forms.CharField(max_length=15, label='Телефон')
    address = forms.CharField(widget=forms.Textarea, label='Адрес')
    telegram_username = forms.CharField(max_length=255, required=False, label='Telegram Username')
    chat_id = forms.CharField(max_length=255, required=False, label='Chat ID')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'phone', 'email', 'address', 'telegram_username', 'chat_id', 'password1', 'password2')

    def save(self, commit=True):
        try:
            user = self.instance
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.phone = self.cleaned_data['phone']
            user.address = self.cleaned_data['address']
            user.telegram_username = self.cleaned_data.get('telegram_username')
            user.chat_id = self.cleaned_data.get('chat_id')

            if commit:
                logger.info(f"Saving user: {user.username}, password set: {bool(user.password)}")
                user.save()
            logger.info(f'User {user.username} has been created/updated successfully.')
            return user
        except Exception as e:
            #logger.error(f'Error saving user: {e}')
            raise

