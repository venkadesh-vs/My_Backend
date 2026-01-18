from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomerCreate(BaseModel):
    user_id: int
    name: str
    phone: str
    email: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None

class CustomerResponse(BaseModel):
    customer_id: int
    user_id: int
    name: str
    phone: str
    email: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True