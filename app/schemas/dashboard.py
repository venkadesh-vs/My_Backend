from pydantic import BaseModel
from decimal import Decimal
from typing import List

class DashboardStatsResponse(BaseModel):
    total_credits: Decimal
    total_payments: Decimal
    outstanding: Decimal
    active_customers: int

class MonthlyData(BaseModel):
    month: str
    credits: float
    payments: float

class TopCustomer(BaseModel):
    name: str
    outstanding: float

class DashboardChartsResponse(BaseModel):
    monthly_data: List[MonthlyData]
    top_customers: List[TopCustomer]