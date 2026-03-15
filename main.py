from fastapi import FastAPI
import uvicorn
from database import database
from config.router import register_routes
# from .config.logging import configure_logging, LogLevels
from .config.middleware import CORSMiddleware, LimitRateHeaderMiddleware


# configure_logging(LogLevels.info)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación. Aquí se pueden realizar tareas de inicialización como crear tablas, cargar datos iniciales, etc."""
    database.Base.metadata.create_all(bind=database.engine)
    print("✅ Base de datos inicializada y tablas creadas")


app.add_middleware(CORSMiddleware)
app.add_middleware(LimitRateHeaderMiddleware)


register_routes(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
