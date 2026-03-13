from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.core import SoftDeleteModel


class Parameter(SoftDeleteModel):
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    editable = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Parameter(id={self.id}, name='{self.name}', value='{self.value}')>"