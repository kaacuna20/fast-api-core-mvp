from pydantic import BaseModel, Field
from typing import Optional, List


class ReadParameter(BaseModel):
    name: str = Field(..., description="Name of the parameter")
    reference: str = Field(..., description="Reference of the parameter")
    description: Optional[str] = Field(None, description="Description of the parameter")
    data: Optional[dict] = Field(None, description="Additional data related to the parameter")


class CreateParameter(BaseModel):
    name: str = Field(..., description="Name of the parameter")
    reference: str = Field(..., description="Reference of the parameter")
    description: Optional[str] = Field(None, description="Description of the parameter")
    data: Optional[dict] = Field(None, description="Additional data related to the parameter")






