from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.core.routes import router as core_router


def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(core_router)