from config.logging import configure_logging, LogLevels
import time


logger =  configure_logging(LogLevels.info)

class DataResponse:
    message: str = ""
    data: dict | list= {}
    status_code: int = 200
    error: str = None


def count_timer(func):
    """Decorator para medir el tiempo de ejecución de una función"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Tiempo de ejecución de {func.__name__}: {end_time - start_time:.2f} segundos")
        return result
    return wrapper


def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """Decorator para reintentar una función en caso de excepción"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Error en {func.__name__}: {e}. Reintentando ({retries + 1}/{max_retries})...")
                    retries += 1
                    time.sleep(delay)
            logger.error(f"Máximo número de reintentos alcanzado para {func.__name__}")
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator


def view_process_resources(func):
    """Decorator para mostrar recursos utilizados por una función (ejemplo de uso)"""
    def wrapper(*args, **kwargs):
        logger.info(f"Recursos antes de ejecutar {func.__name__}: CPU: 10%, Memoria: 100MB")  # Ejemplo estático
        result = func(*args, **kwargs)
        logger.info(f"Recursos después de ejecutar {func.__name__}: CPU: 20%, Memoria: 150MB")  # Ejemplo estático
        return result
    return wrapper
