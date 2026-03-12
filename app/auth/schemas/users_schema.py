from pydantic import BaseModel, EmailStr


class ReadUser(BaseModel):
    email: EmailStr
    password: str

class CreateUser(BaseModel):
    email: EmailStr
    password: str

