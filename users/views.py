from telegram import Bot
from django.views.generic import TemplateView
from django.contrib.auth import login
from django.views import View
from django.shortcuts import render, redirect
from .forms import CustomSignupForm  # Убедитесь, что вы импортируете вашу форму


class CompleteSignupView(View):
    def get(self, request):
        # Проверка параметров в URL
        username = request.GET.get('username')
        chat_id = request.GET.get('chat_id')

        if username and chat_id:
            # Если параметры присутствуют, показываем страницу для завершения регистрации
            form = CustomSignupForm()
            return render(request, 'registration/signup_success.html', {'form': form, 'username': username, 'chat_id': chat_id})
        else:
            # Если параметры отсутствуют, показываем страницу регистрации
            return render(request, 'registration/signup.html')

    def post(self, request):
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            telegram_username = form.cleaned_data.get('telegram_username')
            print(f"Зарегистрированный Telegram Username: {telegram_username}")
            return redirect('index')  # Замените на страницу по умолчанию
        return render(request, 'registration/signup_success.html', {'form': form})



class SignupView(View):
    def get(self, request):
        form = CustomSignupForm()
        return render(request, 'registration/signup.html', {'form': form})

    from django.contrib.auth.hashers import make_password

    def post(self, request):
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 == password2:
                user.set_password(password1)  # Установите пароль пользователя
                user.save()
                login(request, user)
                return redirect('some_default_page')  # Замените на страницу по умолчанию
            else:
                form.add_error(None, "Пароли не совпадают.")
        return render(request, 'registration/signup_success.html', {'form': form})


# Представление для страницы активации через Telegram
class ActivationView(TemplateView):
    template_name = 'registration/telegram_activation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['telegram_username'] = self.kwargs.get('telegram_username')
        return context



# class SignupView(View):
#     def get(self, request):
#         form = CustomSignupForm()
#         return render(request, 'registration/signup.html', {'form': form})
#
#     def post(self, request):
#         form = CustomSignupForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('index')  # Перенаправление на главную страницу
#         return render(request, 'registration/signup.html', {'form': form})  # Возврат к шаблону с ошибками

# class SignupView(View):
#     def get(self, request):
#         form = CustomSignupForm()
#         return render(request, 'users/signup.html', {'form': form})
#
#     def post(self, request):
#         form = CustomSignupForm(request.POST)
#         if form.is_valid():
#             user = form.save()  # Сохраняем пользователя без передачи request
#             login(request, user)
#             return redirect('index')  # Убедитесь, что 'index' соответствует вашему главному маршруту
#         return render(request, 'users/signup.html', {'form': form})
# def send_activation_message(telegram_username):
#     bot = Bot(token='7369326068:AAGIKuTlGEoKO7i48YzgFNLyPKdc946pbSI')
#     try:
#         message = "Привет! Заверши регистрацию, отправив команду /start боту."
#         # Отправляем сообщение по username
#         bot.send_message(chat_id=f"@{telegram_username}", text=message)
#         print(f"Сообщение отправлено пользователю: @{telegram_username}")
#     except Exception as e:
#         print(f"Не удалось отправить сообщение пользователю @{telegram_username}: {e}")