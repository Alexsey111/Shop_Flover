from django import forms
from django.contrib.auth import get_user_model

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CustomSignupForm(UserCreationForm):  # Наследуемся от UserCreationForm
    first_name = forms.CharField(max_length=30, label='Имя')
    last_name = forms.CharField(max_length=30, label='Фамилия')
    phone = forms.CharField(max_length=15, label='Телефон')
    address = forms.CharField(widget=forms.Textarea, label='Адрес')
    telegram_username = forms.CharField(max_length=255, required=False, label='Telegram Username')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'email', 'address', 'telegram_username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.telegram_username = self.cleaned_data['telegram_username']
        if commit:
            user.save()
        return user




# from django import forms
# from django.contrib.auth import get_user_model
#
#
# User = get_user_model()
#
# class CustomSignupForm(forms.Form):
#     first_name = forms.CharField(max_length=30, label='Имя')
#     last_name = forms.CharField(max_length=30, label='Фамилия')
#     phone = forms.CharField(max_length=15, label='Телефон')
#     address = forms.CharField(widget=forms.Textarea, label='Адрес')
#     telegram_username = forms.CharField(max_length=255, required=False, label='Telegram Username')
#
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'phone', 'email', 'address', 'telegram_username', 'password1', 'password2')
#
#     def signup(self, request, user):
#         from allauth.account.forms import SignupForm
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.phone = self.cleaned_data['phone']
#         user.address = self.cleaned_data['address']
#         user.telegram_username = self.cleaned_data['telegram_username']
#         user.save()
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         if commit:
#             user.save()
#         return user



# User = get_user_model()
#
# class CustomSignupForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'phone', 'email', 'address', 'telegram_username', 'password1', 'password2')
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         if commit:
#             user.save()
#         return user
