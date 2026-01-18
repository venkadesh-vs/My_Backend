from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class CreditCreate(BaseModel):
    user_id: int
    customer_id: int
    amount: Decimal
    description: Optional[str] = None
    date: date

class CreditResponse(BaseModel):
    credit_id: int
    user_id: int
    customer_id: int
    customer_name: str
    amount: Decimal
    description: Optional[str] = None
    date: date
    created_at: datetime
    
    class Config:
        from_attributes = True