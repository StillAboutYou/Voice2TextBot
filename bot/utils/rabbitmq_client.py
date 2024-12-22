import pika
import json
from bot.config import config


def publish_to_queue(queue_name: str, message: dict):
    """
    Публикация сообщения в RabbitMQ.
    :param queue_name: Название очереди
    :param message: Сообщение для отправки
    """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),  # Stable message
        )
        connection.close()
    except Exception as e:
        raise RuntimeError(f"Ошибка при отправке сообщения в RabbitMQ: {e}")
