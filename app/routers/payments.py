from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from core.database import get_db
from models.models import Payment, Customer, Credit
from schemas.payment import PaymentCreate, PaymentResponse
from decimal import Decimal

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.get("", response_model=List[PaymentResponse])
def get_payments(user_id: int = Query(...), db: Session = Depends(get_db)):
    payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    
    result = []
    for payment in payments:
        customer = db.query(Customer).filter(Customer.customer_id == payment.customer_id).first()
        payment_dict = {
            "payment_id": payment.payment_id,
            "user_id": payment.user_id,
            "customer_id": payment.customer_id,
            "customer_name": customer.name if customer else "Unknown",
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "date": payment.date,
            "created_at": payment.created_at
        }
        result.append(payment_dict)
    
    return result

@router.post("", response_model=PaymentResponse)
def create_payment(request: PaymentCreate, db: Session = Depends(get_db)):
    # Security check: Verify customer belongs to this user
    customer = db.query(Customer).filter(
        Customer.customer_id == request.customer_id,
        Customer.user_id == request.user_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found or not authorized")
    
    # Calculate customer's total credits
    total_credits = db.query(func.sum(Credit.amount)).filter(
        Credit.customer_id == request.customer_id
    ).scalar() or Decimal(0)
    
    # Calculate customer's total payments (including current payments)
    total_payments = db.query(func.sum(Payment.amount)).filter(
        Payment.customer_id == request.customer_id
    ).scalar() or Decimal(0)
    
    # Calculate outstanding balance
    outstanding = total_credits - total_payments
    
    # Validation: Payment cannot exceed outstanding balance
    if request.amount > outstanding:
        raise HTTPException(
            status_code=400, 
            detail=f"Payment amount (₹{request.amount}) exceeds outstanding balance (₹{outstanding}). Customer can pay maximum ₹{outstanding} only."
        )
    
    # If validation passes, create payment
    new_payment = Payment(
        user_id=request.user_id,
        customer_id=request.customer_id,
        amount=request.amount,
        payment_method=request.payment_method,
        date=request.date
    )
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return {
        "payment_id": new_payment.payment_id,
        "user_id": new_payment.user_id,
        "customer_id": new_payment.customer_id,
        "customer_name": customer.name,
        "amount": new_payment.amount,
        "payment_method": new_payment.payment_method,
        "date": new_payment.date,
        "created_at": new_payment.created_at
    }

@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int, 
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this payment")
    
    db.delete(payment)
    db.commit()
    
    return {"message": "Payment deleted successfully"}