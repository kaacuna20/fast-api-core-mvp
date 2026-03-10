from fastapi import FastAPI
from .database.core import engine, Base
from .entities.todo import Todo  # Import models to register them
from .entities.user import User  # Import models to register them
from .app.routes import register_routes
# from .config.logging import configure_logging, LogLevels
from .config.middleware import CORSMiddleware, LimitRateHeaderMiddleware


# configure_logging(LogLevels.info)

app = FastAPI()

# """ Only uncomment below to create new tables, 
# otherwise the tests will fail if not connected
# """
# # Base.metadata.create_all(bind=engine)

# app.add_middleware(APIKeyMiddleware)
app.add_middleware(CORSMiddleware)
app.add_middleware(LimitRateHeaderMiddleware)


register_routes(app)