import asyncio
import json
import logging
import pika
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ContentType
from bot.config import config
from bot.handlers.voice_handler import handle_voice_message

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Логи в файл
        logging.StreamHandler()          # Логи в консоль
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Регистрация хендлеров
def register_handlers(dp: Dispatcher):
    dp.message.register(
        handle_voice_message,
        lambda message: message.content_type == ContentType.VOICE
    )

register_handlers(dp)

# Хендлер для команды /start
@dp.message(Command("start"))
async def start_command_handler(message: Message):
    await message.reply("Бот запущен. Отправьте голосовое сообщение для обработки.")

# Асинхронный RabbitMQ consumer
async def rabbitmq_consumer():
    loop = asyncio.get_event_loop()

    def consume():
        try:
            # Подключение к RabbitMQ
            logger.info("Подключение к RabbitMQ...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=int(config.RABBITMQ_PORT),
                credentials=pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
            ))
            channel = connection.channel()
            channel.queue_declare(queue=config.RABBITMQ_RESPONSE_QUEUE, durable=True)
            logger.info("Успешное подключение к RabbitMQ")

            # Callback для обработки сообщений из очереди
            def on_message(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    sender_id = data.get("sender_id")
                    recognized_text = data.get("recognized_text")

                    # Асинхронная отправка сообщения пользователю
                    if sender_id and recognized_text:
                        asyncio.run_coroutine_threadsafe(
                            bot.send_message(
                                chat_id=sender_id,
                                text=f"Распознанный текст: {recognized_text}"
                            ), loop=loop
                        )
                        logger.info(f"Сообщение отправлено пользователю {sender_id}: {recognized_text}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Ошибка при обработке сообщения: {e}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            # Запускаем потребление сообщений
            channel.basic_consume(queue=config.RABBITMQ_RESPONSE_QUEUE, on_message_callback=on_message)
            logger.info("RabbitMQ consumer запущен и ожидает сообщения...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {e}")

    # Запускаем блокирующий consumer в отдельном потоке
    await loop.run_in_executor(None, consume)

# Основная функция запуска
async def main():
    logger.info("Запуск бота и RabbitMQ consumer...")
    await asyncio.gather(
        dp.start_polling(bot),  # Запуск aiogram бота
        rabbitmq_consumer()     # Запуск RabbitMQ consumer
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
