from fastapi import FastAPI
from app.auth.v1.routes import router as auth_router_v1
from app.core.v1.routes import router as core_router_v1


def register_routes(app: FastAPI):
    app.include_router(auth_router_v1, prefix="/api/v1/", tags=["auth"])
    app.include_router(core_router_v1, prefix="/api/v1/", tags=["core"])