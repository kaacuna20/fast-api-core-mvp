from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import Depends
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from sqlalchemy.orm import Session
from models.User import User
from schemas.jwt_schema import Token
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from exceptions import AuthenticationError, UserNotFoundError, PasswordMismatchError, InvalidPasswordError
from config.settings import Settings
from config.logging import configure_logging, LogLevels


class AuthService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.SECRET_KEY = self.settings.JWT_SECRET_KEY or '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
        self.ALGORITHM = self.settings.JWT_ALGORITHM or 'HS256'
        self.ACCESS_TOKEN_EXPIRE_MINUTES = self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES or 30
        self.oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
        self.bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.logger = configure_logging(LogLevels.INFO)

    def authenticate_user(self, email: str, password: str, db: Session) -> User | bool:
        user = db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.password):
            self.logger.warning(f"Failed authentication attempt for email: {email}")
            return False
        return user
    
    def create_access_token(self, email: str, user_id: int, expires_delta: timedelta) -> str:
        encode = {
            'sub': email,
            'id': str(user_id),
            'exp': datetime.now(timezone.utc) + expires_delta
        }
        return jwt.encode(encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def get_current_user(self, token: Annotated[str, Depends(self.oauth2_bearer)], db: Session) -> User:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: str = payload.get('id')
            user = db.query(User).filter(User.id == int(user_id)).first()
            if not user:
                raise UserNotFoundError(user_id=user_id)
            return user
        except PyJWTError as e:
            self.logger.warning(f"Token verification failed: {str(e)}")
            raise AuthenticationError()
        
    def login_for_access_token(self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session) -> Token:
        user = self.authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise AuthenticationError()
        token = self.create_access_token(user.email, user.id, timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES))
        return Token(access_token=token, token_type='bearer')


