from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.core import SoftDeleteModel


class Role(SoftDeleteModel):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    users = relationship('User', back_populates='role')
    permissions = relationship('Permission', back_populates='role')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
