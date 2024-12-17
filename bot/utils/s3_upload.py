import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from bot.config import config


async def upload_file_to_minio(file_data, file_name: str) -> str:
    """
    Загрузка файла в Minio.
    :param file_data: Поток данных файла
    :param file_name: Имя файла для сохранения
    :return: URL загруженного файла
    """
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=f"http://{config.MINIO_ENDPOINT}",
            aws_access_key_id=config.MINIO_ACCESS_KEY,
            aws_secret_access_key=config.MINIO_SECRET_KEY,
        )

        s3_client.upload_fileobj(file_data, config.MINIO_BUCKET, file_name)
        return f"http://{config.MINIO_ENDPOINT}/{config.MINIO_BUCKET}/{file_name}"
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise RuntimeError(f"Ошибка при загрузке файла в Minio: {e}")
