from telegram_bot.bot import send_telegram_message
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_order_confirmation(order):
    chat_id = order.user.chat_id
    if not chat_id:
        logger.warning(f"Chat ID отсутствует для пользователя {order.user.username} (ID {order.user.id}).")
        return

    message = f"Ваш заказ #{order.id} подтвержден. Общая сумма: {order.total_price}."
    logger.info(f"Отправка сообщения для заказа {order.id}, пользователю {order.user.username} (chat_id: {chat_id})")

    # Отправка сообщения с использованием await
    await send_telegram_message(chat_id, message)


