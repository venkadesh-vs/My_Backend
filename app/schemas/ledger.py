from pydantic import BaseModel
from typing import List
from datetime import date
from decimal import Decimal

class LedgerTransaction(BaseModel):
    date: date
    description: str
    debit: Decimal
    credit: Decimal
    balance: Decimal

class LedgerResponse(BaseModel):
    customer_name: str
    transactions: List[LedgerTransaction]
    outstanding_balance: Decimal