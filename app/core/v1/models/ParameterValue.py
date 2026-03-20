from sqlalchemy import Column, Integer, String, Boolean, JSON, Text, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.core import SoftDeleteModel


class ParameterValue(SoftDeleteModel):
    __tablename__ = 'parameter_values'

    id = Column(Integer, primary_key=True, index=True)
    parameter_id = Column(Integer, ForeignKey('parameters.id'), nullable=False)
    parent_id = Column(Integer, ForeignKey('parameter_values.id'), nullable=True)  # Para valores jerárquicos
    value = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    data =  Column(JSON, nullable=True)  # Para almacenar datos adicionales relacionados con el valor
    is_active = Column(Boolean, default=True)

    parameter = relationship('Parameter', back_populates='values')
    parent = relationship('ParameterValue', remote_side=[id], back_populates='children')
    children = relationship('ParameterValue', back_populates='parent', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<ParameterValue(id={self.id}, parameter_id={self.parameter_id}, value='{self.value}')>"