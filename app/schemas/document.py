from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Shared base properties
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: str
    file_type: str = "url"
    file_size: Optional[int] = 0
    project_id: int

# Properties to receive on creation
class DocumentCreate(DocumentBase):
    pass

# Properties to receive on update
class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None

# Base user representation for response
class DocumentUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    
    class Config:
        from_attributes = True

# Properties to return to client
class DocumentResponse(DocumentBase):
    id: int
    uploaded_by_id: Optional[int] = None
    uploaded_by: Optional[DocumentUser] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
