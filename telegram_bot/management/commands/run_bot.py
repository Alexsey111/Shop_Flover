from django.core.management.base import BaseCommand
from telegram_bot.bot import main  # Импортируем основную функцию запуска бота

class Command(BaseCommand):
    help = 'Запуск Telegram бота'

    def handle(self, *args, **kwargs):
        main()
