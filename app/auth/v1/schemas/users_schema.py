from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class ReadUser(BaseModel):
    email: EmailStr
    password: str
    is_active: bool = Field(default=True, description="User's active status")
    role_id: Optional[int] = None

class CreateUser(BaseModel):
    email: EmailStr
    password: str
    role_id: int
    api_key: str = None

