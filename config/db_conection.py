from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from config.settings import Settings
from enum import StrEnum


settings = Settings()


class DBEngines(StrEnum):
    sqlite = "sqlite"
    postgresql = "postgresql"
    mysql = "mysql"


class Database:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def _get_database_url(self) -> str:
        """Construye la URL de conexión según el motor de base de datos"""
        if self.settings.DB_ENGINE == DBEngines.sqlite:
            return f"sqlite:///{self.settings.DB_NAME}.db"
        
        elif self.settings.DB_ENGINE == DBEngines.postgresql:
            return (
                f"postgresql://{self.settings.DB_USER}:{self.settings.DB_PASSWORD}"
                f"@{self.settings.DB_HOST}:{self.settings.DB_PORT}/{self.settings.DB_NAME}"
            )
        
        elif self.settings.DB_ENGINE == DBEngines.mysql:
            return (
                f"mysql+pymysql://{self.settings.DB_USER}:{self.settings.DB_PASSWORD}"
                f"@{self.settings.DB_HOST}:{self.settings.DB_PORT}/{self.settings.DB_NAME}"
            )
        
        else:
            raise ValueError(
                f"Unsupported DB_ENGINE: {self.settings.DB_ENGINE}. "
                f"Supported engines: {', '.join([e.value for e in DBEngines])}"
            )
        
    def render_database_url(self) -> str:
        """Método para obtener la URL de la base de datos (útil para debugging)"""
        return self._get_database_url()

    def _create_engine(self):
        """Crea el engine de SQLAlchemy con la configuración apropiada"""
        database_url = self._get_database_url()
        
        # Configuración específica para SQLite
        if self.settings.DB_ENGINE == DBEngines.sqlite:
            return create_engine(
                database_url,
                connect_args={"check_same_thread": False}
            )
        
        # Otras bases de datos (PostgreSQL, MySQL)
        return create_engine(database_url)

    def get_db(self) -> Session:
        """Generador de sesiones para usar con FastAPI Depends"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()




