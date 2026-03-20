from sqlalchemy import Column, String, Boolean, JSON, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from database.core import BaseModel


class Permission(BaseModel):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(50), unique=True, nullable=False)
    service = Column(String(50), nullable=False)  # The service or resource this permission applies to
    module = Column(String(50), nullable=False)  # The module or feature this permission applies to
    actions = Column(JSON, nullable=False)  # List of allowed actions (e.g., ["create", "read", "update", "delete"])
    is_active = Column(Boolean, default=True)
    role_reference = Column(String(50), ForeignKey('roles.reference'), nullable=False)

    role = relationship('Role', back_populates='permissions')

    __table_args__ = (
        UniqueConstraint('service', 'module','role_reference', name='uq_service_module_role_reference'),
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"