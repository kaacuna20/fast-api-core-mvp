import boto3
import os
from botocore.exceptions import NoCredentialsError
from config.settings import Settings
from abc import ABC, abstractmethod
from enum import StrEnum


class StorageTypes(StrEnum):
    local = "local"
    s3 = "s3"


class Storage(ABC):
    """Interfaz para el sistema de almacenamiento"""
    
    @abstractmethod
    def save_file(self, file_path: str, destination_path: str) -> str:
        """Guarda un archivo y devuelve su URL o ruta de acceso"""
        pass

    @abstractmethod
    def load_file(self, file_path: str, destination_path: str) -> str:
        """Carga un archivo desde la ubicación de almacenamiento"""
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        """Elimina un archivo del almacenamiento"""
        pass


class LocalStorage(Storage):
    """Implementación de almacenamiento local"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
    
    def save_file(self, file_path: str, destination_path: str) -> str:
        full_destination = os.path.join(self.base_path, destination_path)
        os.makedirs(os.path.dirname(full_destination), exist_ok=True)
        os.rename(file_path, full_destination)
        return full_destination
    
    def load_file(self, file_path: str, destination_path: str) -> str:
        full_path = os.path.join(self.base_path, file_path)
        if os.path.exists(full_path):
            os.rename(full_path, destination_path)
            return destination_path
        else:
            raise FileNotFoundError(f"File not found: {full_path}")
    
    def delete_file(self, file_path: str) -> None:
        full_path = os.path.join(self.base_path, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)


class S3Storage(Storage):
    """Implementación de almacenamiento en S3"""
    
    def __init__(self, bucket_name: str, access_key: str, secret_key: str, region: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
    
    def save_file(self, file_path: str, destination_path: str) -> str:
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, destination_path)
            url = f"https://{self.bucket_name}.s3.{self.s3_client.meta.region_name}.amazonaws.com/{destination_path}"
            return url
        except NoCredentialsError:
            raise Exception("AWS credentials not provided or invalid")
        
    def load_file(self, file_path, destination_path):
        return super().load_file(file_path, destination_path)
    
    def delete_file(self, file_path: str) -> None:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
        except NoCredentialsError:
            raise Exception("AWS credentials not provided or invalid")


class StorageFactory:
    """Fábrica para crear instancias de almacenamiento según la configuración"""
    
    @staticmethod
    def create_storage(settings: Settings) -> Storage:
        if settings.FYLESYSTEM == StorageTypes.s3:
            return S3Storage(
                bucket_name=settings.S3_BUCKET_NAME,
                access_key=settings.S3_ACCESS_KEY,
                secret_key=settings.S3_SECRET_KEY,
                region=settings.S3_REGION
            )
        else:
            return LocalStorage(base_path=settings.FYLESYSTEM_LOCAL_STORAGE_PATH)