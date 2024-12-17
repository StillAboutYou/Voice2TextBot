import pika
import json
import logging
from core.database import save_recognized_text
from core.minio_client import download_file_from_minio
import whisper
from bot.config import config
from botocore.exceptions import ClientError
import tempfile

# Настройка логирования
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Загрузка модели Whisper
logger.info("Загрузка модели Whisper...")
model = whisper.load_model("small", device="cpu")
logger.info("Модель Whisper загружена.")

def process_task(ch, method, properties, body):
    try:
        task = json.loads(body)
        sender_id = task.get("sender_id")
        message_id = task.get("message_id")
        bucket_name = task.get("bucket_name")
        file_name = task.get("file_name")

        if not sender_id or not message_id or not bucket_name or not file_name:
            raise ValueError("Отсутствуют обязательные поля в задаче")

        voice_url = f"http://{config.MINIO_ENDPOINT}/{bucket_name}/{file_name}"
        logger.info(f"Получена задача: sender_id={sender_id}, message_id={message_id}, voice_url={voice_url}")

        # Загрузка файла
        audio_data = download_file_from_minio(bucket_name, file_name)

        # Распознавание текста
        with tempfile.NamedTemporaryFile(suffix=".ogg") as tmp_file:
            tmp_file.write(audio_data.getvalue())
            tmp_file.flush()
            result = model.transcribe(tmp_file.name)
            recognized_text = result.get("text", "").strip()
            logger.info(f"Распознанный текст: {recognized_text}")

        if not recognized_text:
            raise ValueError("Распознанный текст пуст")

        # Сохранение в базу данных
        save_recognized_text(sender_id, voice_url, recognized_text)

        # Отправка результата обратно через RabbitMQ
        response_message = {
            "sender_id": sender_id,
            "message_id": message_id,
            "recognized_text": recognized_text,
        }

        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=config.RABBITMQ_RESPONSE_QUEUE, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=config.RABBITMQ_RESPONSE_QUEUE,
            body=json.dumps(response_message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()

        logger.info(f"Ответ отправлен: {response_message}")

        # Подтверждаем обработку сообщения
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Ошибка при обработке задачи: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_HOST))
        channel = connection.channel()

        # Подписываемся на очередь
        channel.queue_declare(queue=config.RABBITMQ_QUEUE, durable=True)
        channel.basic_consume(queue=config.RABBITMQ_QUEUE, on_message_callback=process_task)

        logger.info("Ожидание сообщений...")
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Consumer остановлен.")
    except Exception as e:
        logger.error(f"Ошибка consumer: {e}")

if __name__ == "__main__":
    start_consumer()
