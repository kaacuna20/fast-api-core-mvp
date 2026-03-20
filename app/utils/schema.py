from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from .helper import to_camel





class CustomBaseModel(BaseModel):
    """Base model for all schemas"""
    class Config:
        orm_mode = True
        alias_generator = to_camel
        populate_by_field_name = True
        allow_population_by_alias = True
        json_encoders = {
            datetime: datetime.isoformat,
            Decimal: float,
            
        }

