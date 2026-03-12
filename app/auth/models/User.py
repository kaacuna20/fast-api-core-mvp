from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.core import SoftDeleteModel


class User(SoftDeleteModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)