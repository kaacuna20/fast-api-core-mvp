from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.core import SoftDeleteModel


class ActivityLog(SoftDeleteModel):
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True, index=True)
    log_name = Column(String(255), nullable=False)
    module = Column(String(255), nullable=True)
    service = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # Para almacenar datos adicionales relacionados con la actividad
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    user = relationship('User', back_populates='activity_logs')

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, log_name='{self.log_name}', module='{self.module}', service='{self.service}', user_id={self.user_id}, action='{self.action}', timestamp='{self.timestamp}')>"
