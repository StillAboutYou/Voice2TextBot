from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Загружаем переменные окружения из .env файла
load_dotenv("../.env")


class Config(BaseSettings):
    # Telegram Bot API token
    BOT_TOKEN: str

    # Minio settings
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str

    # PostgreSQL settings
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # RabbitMQ settings
    RABBITMQ_HOST: str
    RABBITMQ_PORT: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_QUEUE: str
    RABBITMQ_RESPONSE_QUEUE: str  # Очередь для отправки результатов

    IS_LOCAL: bool

    @property
    def DATABASE_URL(self):
        if bool(self.IS_LOCAL):
            return (
                f"postgresql://{self.POSTGRES_USER}:" +
                f"{self.POSTGRES_PASSWORD}" +
                f"@postgres:5432/{self.POSTGRES_DB}"
            )
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@" +
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    class Config:
        env_file = "../.env"


config = Config()
