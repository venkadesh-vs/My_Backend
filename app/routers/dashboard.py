from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from core.database import get_db
from models.models import Credit, Payment, Customer
from schemas.dashboard import DashboardStatsResponse, DashboardChartsResponse
from decimal import Decimal
from datetime import datetime

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(user_id: int = Query(...), db: Session = Depends(get_db)):
    total_credits = db.query(func.sum(Credit.amount)).filter(Credit.user_id == user_id).scalar()
    total_credits = total_credits or Decimal(0)
    
    total_payments = db.query(func.sum(Payment.amount)).filter(Payment.user_id == user_id).scalar()
    total_payments = total_payments or Decimal(0)
    
    outstanding = total_credits - total_payments
    
    active_customers = db.query(Customer).filter(Customer.user_id == user_id).count()
    
    return {
        "total_credits": total_credits,
        "total_payments": total_payments,
        "outstanding": outstanding,
        "active_customers": active_customers
    }

@router.get("/charts", response_model=DashboardChartsResponse)
def get_dashboard_charts(user_id: int = Query(...), db: Session = Depends(get_db)):
    current_year = datetime.now().year
    
    monthly_credits = db.query(
        extract('month', Credit.date).label('month'),
        func.sum(Credit.amount).label('total')
    ).filter(
        Credit.user_id == user_id,
        extract('year', Credit.date) == current_year
    ).group_by(
        extract('month', Credit.date)
    ).all()
    
    monthly_payments = db.query(
        extract('month', Payment.date).label('month'),
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.user_id == user_id,
        extract('year', Payment.date) == current_year
    ).group_by(
        extract('month', Payment.date)
    ).all()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data = []
    
    credits_dict = {int(row.month): float(row.total) for row in monthly_credits}
    payments_dict = {int(row.month): float(row.total) for row in monthly_payments}
    
    for month_num in range(1, 13):
        monthly_data.append({
            "month": month_names[month_num - 1],
            "credits": credits_dict.get(month_num, 0),
            "payments": payments_dict.get(month_num, 0)
        })
    
    customers = db.query(Customer).filter(Customer.user_id == user_id).all()
    
    top_customers_data = []
    for customer in customers:
        customer_credits = db.query(func.sum(Credit.amount)).filter(
            Credit.customer_id == customer.customer_id
        ).scalar() or Decimal(0)
        
        customer_payments = db.query(func.sum(Payment.amount)).filter(
            Payment.customer_id == customer.customer_id
        ).scalar() or Decimal(0)
        
        outstanding = float(customer_credits - customer_payments)
        
        if outstanding > 0:
            top_customers_data.append({
                "name": customer.name,
                "outstanding": outstanding
            })
    
    top_customers_data.sort(key=lambda x: x['outstanding'], reverse=True)
    top_customers = top_customers_data[:5]
    
    return {
        "monthly_data": monthly_data,
        "top_customers": top_customers
    }