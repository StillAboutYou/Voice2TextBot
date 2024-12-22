import io
import asyncio
from aiogram import Bot
from aiogram.types import Message
from bot.config import config
from bot.utils.rabbitmq_client import publish_to_queue
from aiogram.exceptions import TelegramBadRequest


async def get_file_with_retries(bot: Bot, file_id: str,
                                retries: int = 3, delay: int = 2):
    """
    Получение файла с повторами при временной недоступности.
    :param bot: Объект бота
    :param file_id: ID файла
    :param retries: Количество попыток
    :param delay: Задержка между попытками
    :return: Объект файла
    """
    for attempt in range(retries):
        try:
            return await bot.get_file(file_id)
        except TelegramBadRequest as e:
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise e


async def handle_voice_message(message: Message, bot: Bot):
    """
    Обработчик голосовых сообщений.
    """
    if not message.voice:
        await message.answer("Это не голосовое сообщение.")
        return

    try:
        voice = message.voice

        # Попытка получения файла с повторами
        file = await get_file_with_retries(bot, voice.file_id)

        if not file.file_path:
            await message.answer("Файл временно недоступен. Попробуйте позже.")
            return

        # Загружаем файл в память через download_file
        file_data = io.BytesIO()
        await bot.download_file(file.file_path, destination=file_data)
        file_data.seek(0)

        # Загрузка в Minio
        file_name = f"{message.from_user.id}/{message.message_id}.ogg"
        # voice_url = await upload_file_to_minio(file_data, file_name)

        # Отправка в очередь
        task = {
            "sender_id": message.from_user.id,
            "message_id": message.message_id,
            "bucket_name": config.MINIO_BUCKET,
            "file_name": file_name,
        }
        publish_to_queue(config.RABBITMQ_QUEUE, task)

        await message.answer("Ваше сообщение отправлено на обработку!")

    except TelegramBadRequest as e:
        await message.answer(f"Ошибка Telegram: {e.message}")
    except asyncio.TimeoutError:
        await message.answer("Превышено время ожидания. Попробуйте позже.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
