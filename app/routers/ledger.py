from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Credit, Payment, Customer
from app.schemas.ledger import LedgerResponse, LedgerTransaction
from decimal import Decimal

router = APIRouter(prefix="/api/ledger", tags=["Ledger"])

@router.get("/{customer_id}", response_model=LedgerResponse)
def get_ledger(customer_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id,
        Customer.user_id == user_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found or not authorized")
    
    credits = db.query(Credit).filter(Credit.customer_id == customer_id).all()
    payments = db.query(Payment).filter(Payment.customer_id == customer_id).all()
    
    transactions = []
    
    for credit in credits:
        transactions.append({
            "date": credit.date,
            "description": credit.description or "Credit entry",
            "debit": credit.amount,
            "credit": Decimal(0),
            "type": "credit",
            "sort_order": 0
        })
    
    for payment in payments:
        transactions.append({
            "date": payment.date,
            "description": f"Payment ({payment.payment_method})",
            "debit": Decimal(0),
            "credit": payment.amount,
            "type": "payment",
            "sort_order": 1
        })
    
    transactions.sort(key=lambda x: (x["date"], x["sort_order"]))
    
    balance = Decimal(0)
    ledger_transactions = []
    
    for transaction in transactions:
        balance += transaction["debit"]
        balance -= transaction["credit"]
        
        ledger_transactions.append(LedgerTransaction(
            date=transaction["date"],
            description=transaction["description"],
            debit=transaction["debit"],
            credit=transaction["credit"],
            balance=balance
        ))
    
    return LedgerResponse(
        customer_name=customer.name,
        transactions=ledger_transactions,
        outstanding_balance=balance
    )