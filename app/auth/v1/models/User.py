from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.core import SoftDeleteModel
from models.Role import Role


class User(SoftDeleteModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)

    # Relaciones
    role = relationship('Role', back_populates='users')
    api_key = relationship('ApiKey', back_populates='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role_id={self.role_id})>"