from pydantic import BaseModel, EmailStr


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
