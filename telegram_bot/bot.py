from django.contrib.auth import get_user_model
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from products.models import Order
from django.utils import timezone
from datetime import timedelta
import logging
from asgiref.sync import sync_to_async
from users.models import CustomUser
import traceback


User = get_user_model()
TOKEN = '7369326068:AAGIKuTlGEoKO7i48YzgFNLyPKdc946pbSI'

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем переменную application глобально
application = Application.builder().token(TOKEN).build()

async def check_profile(chat_id):
    try:
        logger.debug(f"Checking profile with chat_id: {chat_id}")
        profile = await sync_to_async(CustomUser.objects.get)(chat_id=chat_id)
        logger.debug(f"Profile found for chat_id: {chat_id}")
        return profile
    except CustomUser.DoesNotExist:
        logger.error(f"No profile found for chat_id: {chat_id}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    telegram_username = update.message.from_user.username

    # Проверяем, есть ли пользователь с таким chat_id
    user = await sync_to_async(CustomUser.objects.filter(chat_id=chat_id).first)()

    if user:
        logger.debug(f"User found: {telegram_username} with chat_id: {chat_id}")
        # Формируем сообщение с доступными командами
        commands_message = (
            "Добро пожаловать! Вы уже зарегистрированы. Вот список доступных команд:\n"
            "/orders - Получить список ваших заказов\n"
            "/order_status <order_id> - Получить статус заказа\n"
            "/generate_report - Получить отчет о заказах за последние 30 дней\n"
            "Также вы можете перейти на главную страницу проекта: http://127.0.0.1:8000"
        )
        await update.message.reply_text(commands_message)
    else:
        logger.debug(f"No user found with chat_id: {chat_id}")
        await update.message.reply_text("Вы не зарегистрированы. Пожалуйста, используйте команду /register для регистрации.")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    telegram_username = update.message.from_user.username

    # Проверяем, передаются ли значения
    print(f"Received chat_id: {chat_id}, telegram_username: {telegram_username}")

    # Далее код для создания или обновления пользователя
    user, created = await sync_to_async(CustomUser.objects.get_or_create)(
        chat_id=chat_id,
        defaults={'telegram_username': telegram_username}
    )

    if created:
        link = f"http://127.0.0.1:8000/users/signup/?username={telegram_username}&chat_id={chat_id}"
        await update.message.reply_text(f"Перейдите по ссылке для завершения регистрации: {link}")
    else:
        await update.message.reply_text("Вы уже зарегистрированы!")



# Получение списка заказов
async def handle_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)  # Получаем chat_id из сообщения
    logger.info(f"Fetching orders for user with chat_id: {chat_id}")

    try:
        # Найти профиль по chat_id
        profile = await sync_to_async(CustomUser.objects.get)(chat_id=chat_id)
        logger.info(f"Profile found for chat_id {chat_id}: {profile}")

        # Получить заказы для пользователя
        orders = await sync_to_async(list)(Order.objects.filter(user=profile).select_related('user'))

        if not orders:
            await update.message.reply_text('У вас нет заказов.')
        else:
            response = "Ваши заказы:\n"
            for order in orders:
                response += (
                    f"Заказ ID: {order.id}\n"
                    f"Дата: {order.created_at}\n"
                    f"Сумма: {order.total_price}\n"
                    f"Доставка: {order.delivery_option}\n"
                    f"Оплата: {order.payment_option}\n"
                    f"Статус: {order.get_status_display()}\n\n"
                )
            await update.message.reply_text(response)
    except CustomUser.DoesNotExist:
        await update.message.reply_text('Ваш профиль не найден.')
    except Exception as e:
        logger.error(f"Error while fetching orders for user with chat_id {chat_id}: {str(e)}")
        logger.error(traceback.format_exc())
        await update.message.reply_text('Произошла ошибка при получении списка заказов.')


# Получение статуса заказа
async def handle_order_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)

    # Извлечение order_id из текста сообщения
    if context.args:
        try:
            order_id = int(context.args[0])  # Предполагается, что первый аргумент - это ID заказа
        except ValueError:
            await update.message.reply_text("Пожалуйста, укажите действительный ID заказа.")
            return
    else:
        await update.message.reply_text("Пожалуйста, укажите ID заказа.")
        return

    try:
        # Найти профиль по chat_id
        profile = await sync_to_async(CustomUser.objects.get)(chat_id=chat_id)
        logger.info(f"Profile found for chat_id {chat_id}: {profile}")

        # Получить заказ по ID и пользователю
        order = await sync_to_async(Order.objects.select_related('user').get)(id=order_id, user=profile)

        response = (
            f"Заказ ID: {order.id}\n"
            f"Дата: {order.created_at}\n"
            f"Сумма: {order.total_price}\n"
            f"Доставка: {order.delivery_option}\n"
            f"Оплата: {order.payment_option}\n"
            f"Статус: {order.get_status_display()}"
        )
        await update.message.reply_text(response)

    except Order.DoesNotExist:
        await update.message.reply_text("Заказ не найден или вы не имеете доступа к этому заказу.")
    except CustomUser.DoesNotExist:
        await update.message.reply_text("Профиль пользователя не найден.")
    except Exception as e:
        logger.error(f"Error while fetching order status for order ID {order_id} and chat_id {chat_id}: {str(e)}")
        logger.error(traceback.format_exc())
        await update.message.reply_text("Произошла ошибка при получении статуса заказа.")



# Генерация отчета
async def handle_generate_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    one_month_ago = timezone.now() - timedelta(days=30)
    logger.info("Generating report for orders created in the last 30 days.")

    try:
        orders = await sync_to_async(list)(Order.objects.filter(created_at__gte=one_month_ago))

        if not orders:
            await update.message.reply_text("За последние 30 дней заказов не было.")
            return

        report = "Отчет о заказах за последние 30 дней:\n\n"
        for order in orders:
            report += (
                f"Заказ ID: {order.id}\n"
                f"Дата: {order.created_at}\n"
                f"Сумма: {order.total_price}\n"
                f"Доставка: {order.delivery_option}\n"
                f"Оплата: {order.payment_option}\n"
                f"Статус: {order.get_status_display()}\n\n"
            )

        await update.message.reply_text(report)
    except Exception as e:
        logger.error(f"Error while generating report: {str(e)}")
        logger.error(traceback.format_exc())
        await update.message.reply_text("Произошла ошибка при создании отчета.")


async def send_telegram_message(application, chat_id, message):
    if not chat_id or not message:
        logging.error("chat_id или message не определены")
        return

    logging.info(f"Отправка сообщения на chat ID: {chat_id}")

    try:
        # Использование application.bot для отправки сообщения
        await application.bot.send_message(chat_id=chat_id, text=message)
        logging.info("Сообщение успешно отправлено.")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {str(e)}")

# Основная функция для запуска бота
def main():
    global application  # Делаем application глобальной переменной
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("orders", handle_orders_command))
    application.add_handler(CommandHandler("order_status", handle_order_status_command))
    application.add_handler(CommandHandler("generate_report", handle_generate_report_command))

    application.run_polling()

if __name__ == '__main__':
    main()


# async def send_telegram_message(chat_id, message):
#     if not chat_id or not message:
#         logging.error("chat_id или message не определены")
#         return
#
#     logging.info(f"Отправка сообщения на chat ID: {chat_id}")
#
#     try:
#         # Использование application.bot для отправки сообщения
#         await application.bot.send_message(chat_id=chat_id, text=message)
#         logging.info("Сообщение успешно отправлено.")
#     except Exception as e:
#         logging.error(f"Ошибка при отправке сообщения: {str(e)}")
#
#
#
# # Основная функция для запуска бота
# def main():
#     global application  # Делаем application глобальной переменной
#     application = Application.builder().token(TOKEN).build()
#
#     # Регистрация обработчиков команд
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(CommandHandler("register", register))
#     application.add_handler(CommandHandler("orders", handle_orders_command))
#     application.add_handler(CommandHandler("order_status", handle_order_status_command))
#     application.add_handler(CommandHandler("generate_report", handle_generate_report_command))
#
#     application.run_polling()
#
# if __name__ == '__main__':
#     main()

