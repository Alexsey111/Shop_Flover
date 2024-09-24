from django.contrib.auth import get_user_model
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

User = get_user_model()
TOKEN = '7369326068:AAGIKuTlGEoKO7i48YzgFNLyPKdc946pbSI'


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Используйте команду /register для регистрации.")


async def register(update: Update, context: CallbackContext):
    user = update.message.from_user
    # Сохраните имя пользователя и chat_id, например, в базе данных
    username = user.username
    chat_id = user.id

    # Сформируйте ссылку на страницу продолжения регистрации
    link = f"http://127.0.0.1:8000/users/signup/?username={username}&chat_id={chat_id}"
    await update.message.reply_text(f"Пожалуйста, перейдите по следующей ссылке для продолжения регистрации: {link}")


# Основная функция для запуска бота
def main():
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))

    application.run_polling()


if __name__ == '__main__':
    main()
