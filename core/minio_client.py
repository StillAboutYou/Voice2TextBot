import boto3
from bot.config import config
import io

# Инициализация клиента Minio
s3_client = boto3.client(
    's3',
    endpoint_url=f"http://{config.MINIO_ENDPOINT}",  # Например: "http://localhost:9000"
    aws_access_key_id=config.MINIO_ACCESS_KEY,
    aws_secret_access_key=config.MINIO_SECRET_KEY,
    region_name='us-east-1'  # Можно указать любой регион или опустить, если не требуется
)

def download_file_from_minio(bucket_name, file_name):
    """
    Скачивает файл из Minio и возвращает его содержимое как объект BytesIO.
    :param bucket_name: Название бакета в Minio.
    :param file_name: Имя файла.
    :return: BytesIO объект с данными файла.
    """
    import io

    file_data = io.BytesIO()
    s3_client.download_fileobj(bucket_name, file_name, file_data)
    file_data.seek(0)
    return file_data
