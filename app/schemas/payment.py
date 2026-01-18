from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    user_id: int
    customer_id: int
    amount: Decimal
    payment_method: str
    date: date

class PaymentResponse(BaseModel):
    payment_id: int
    user_id: int
    customer_id: int
    customer_name: str
    amount: Decimal
    payment_method: str
    date: date
    created_at: datetime
    
    class Config:
        from_attributes = True