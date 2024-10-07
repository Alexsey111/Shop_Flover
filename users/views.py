from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomSignupForm
from django.views.generic import TemplateView
import logging
from .models import CustomUser
from django.shortcuts import get_object_or_404


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompleteSignupView(View):
    def get(self, request, *args, **kwargs):
        chat_id = request.GET.get('chat_id')
        telegram_username = request.GET.get('username')
        print(f"Chat ID: {chat_id}, Username: {telegram_username}")

        if telegram_username and chat_id:
            form = CustomSignupForm(initial={
                'telegram_username': telegram_username,
                'chat_id': chat_id
            })
            return render(request, 'registration/signup_success.html', {
                'form': form,
                'telegram_username': telegram_username,
                'chat_id': chat_id
            })
        else:
            return render(request, 'registration/signup.html')

    def post(self, request, *args, **kwargs):
        chat_id = request.POST.get('chat_id')
        user = get_object_or_404(CustomUser, chat_id=chat_id)
        form = CustomSignupForm(request.POST, instance=user)

        if form.is_valid():
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 == password2:
                user = form.save(commit=False)
                user.set_password(password1)  # Устанавливаем пароль
                user.save()  # Сохраняем пользователя
                login(request, user)
                return redirect('index')
            else:
                form.add_error('password2', "Введенные пароли не совпадают.")
        else:
            logger.warning(f'Form errors: {form.errors}')  # Логируем ошибки формы

        return render(request, 'registration/signup_success.html', {
            'form': form,
            'chat_id': chat_id,
            'telegram_username': user.telegram_username
        })


class SignupView(View):
    def get(self, request):
        telegram_data = request.session.get('telegram_data')
        form = CustomSignupForm(initial=telegram_data or {})
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            # Проверяем совпадение паролей
            if password1 == password2:
                user.set_password(password1)
                user.save()
                login(request, user)
                return redirect('index')  #
            else:
                form.add_error(None, "Пароли не совпадают.")
        return render(request, 'registration/signup.html', {'form': form})

class ActivationView(TemplateView):
    template_name = 'registration/telegram_activation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['telegram_username'] = self.kwargs.get('telegram_username')
        return context


