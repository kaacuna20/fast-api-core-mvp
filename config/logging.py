import logging
import os
import json
from datetime import datetime
from pathlib import Path
from enum import StrEnum
from logging.handlers import TimedRotatingFileHandler
from config.settings import Settings

settings = Settings()


class JsonFormatter(logging.Formatter):
    """Formateador personalizado para logs en formato JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Agregar campos extra si existen
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


class LogLevels(StrEnum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


def configure_logging(log_level: str = LogLevels.ERROR) -> logging.Logger:
    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        log_level = LogLevels.ERROR

    # Crear directorio de logs si no existe
    log_dir = Path(__file__).parent.parent / "storage" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Nombre del archivo con fecha (ahora .json)
    log_filename = f"app_{datetime.now().strftime('%Y-%m-%d')}.json"
    log_filepath = log_dir / log_filename

    # Configurar el logger raíz
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Limpiar handlers existentes
    logger.handlers.clear()

    # Handler para archivo con rotación diaria (formato JSON)
    file_handler = TimedRotatingFileHandler(
        filename=log_filepath,
        when='midnight',
        interval=1,
        backupCount=30,  # Mantener logs de los últimos 30 días
        encoding='utf-8'
    )
    file_handler.suffix = "%Y-%m-%d.json"
    file_handler.setFormatter(JsonFormatter())
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    # Handler para consola (formato texto)
    console_handler = logging.StreamHandler()
    if log_level == LogLevels.DEBUG:
        console_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT_DEBUG))
    else:
        console_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT_CONSOLE))
    
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    logger.info(f"Logging configurado. Nivel: {log_level}. Archivo: {log_filepath}")
    
    return logger