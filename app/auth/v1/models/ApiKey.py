from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.core import SoftDeleteModel


class ApiKey(SoftDeleteModel):
    """
    Modelo para API Keys con relación 1-1 con User.
    Cada usuario puede tener una única API key activa.
    """
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, index=True)
    # Relación 1-1 con User (unique=True garantiza que cada usuario tenga solo una API key)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False, index=True)
    # Hash de la API key (nunca guardar la key en texto plano)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    key_prefix = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    user = relationship('User', back_populates='api_key', uselist=False)

    def __repr__(self):
        return f"<ApiKey(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
    
    def is_valid(self) -> bool:
        """Verifica si la API key es válida (activa y no expirada)"""
        from datetime import datetime
        
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < datetime.now():
            return False
        
        return True