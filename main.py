from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.settings import Settings
from database import database
from config.router import register_routes
# from .config.logging import configure_logging, LogLevels
from .config.middleware import CORSMiddleware, LimitRateHeaderMiddleware


# configure_logging(LogLevels.info)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Evento que se ejecuta al iniciar la aplicación. Aquí se pueden realizar tareas de inicialización como crear tablas, cargar datos iniciales, etc."""
    database.Base.metadata.create_all(bind=database.engine)
    print("✅ Base de datos inicializada y tablas creadas")
    yield
    # Cleanup al cerrar la aplicación (opcional)
    print("👋 Aplicación cerrándose")

app = FastAPI(lifespan=lifespan)


# @app.on_event("startup")
# async def startup_event():
#     """Evento que se ejecuta al iniciar la aplicación. Aquí se pueden realizar tareas de inicialización como crear tablas, cargar datos iniciales, etc."""
#     database.Base.metadata.create_all(bind=database.engine)
#     print("✅ Base de datos inicializada y tablas creadas")

@app.get("/")
async def root():
    return {
            "message": f"Welcome to the {Settings.APP_API_NAME} application!",
                "current_version": Settings.APP_API_VERSION,
                "versions": {
                    "v1": "/api/v1"
                }
        }

app.add_middleware(CORSMiddleware)
app.add_middleware(LimitRateHeaderMiddleware)


register_routes(app)

