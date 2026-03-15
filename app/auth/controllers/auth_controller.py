from services.auth_service import AuthService
from config.settings import Settings

settings = Settings()


class AuthController:
    def __init__(self):
        self.auth_service = AuthService(settings=settings)

    # Aquí puedes agregar métodos para manejar las rutas de autenticación, por ejemplo:
    # async def login(self, credentials: LoginRequest) -> LoginResponse:
    #     return await self.auth_service.login(credentials)
