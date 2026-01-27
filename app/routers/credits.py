from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.models import Credit, Customer
from schemas.credit import CreditCreate, CreditResponse

router = APIRouter(prefix="/api/credits", tags=["Credits"])

@router.get("", response_model=List[CreditResponse])
def get_credits(user_id: int = Query(...), db: Session = Depends(get_db)):
    credits = db.query(Credit).filter(Credit.user_id == user_id).all()
    
    result = []
    for credit in credits:
        customer = db.query(Customer).filter(Customer.customer_id == credit.customer_id).first()
        credit_dict = {
            "credit_id": credit.credit_id,
            "user_id": credit.user_id,
            "customer_id": credit.customer_id,
            "customer_name": customer.name if customer else "Unknown",
            "amount": credit.amount,
            "description": credit.description,
            "date": credit.date,
            "created_at": credit.created_at
        }
        result.append(credit_dict)
    
    return result

@router.post("", response_model=CreditResponse)
def create_credit(request: CreditCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(
        Customer.customer_id == request.customer_id,
        Customer.user_id == request.user_id
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found or not authorized")
    
    new_credit = Credit(
        user_id=request.user_id,
        customer_id=request.customer_id,
        amount=request.amount,
        description=request.description,
        date=request.date
    )
    
    db.add(new_credit)
    db.commit()
    db.refresh(new_credit)
    
    return {
        "credit_id": new_credit.credit_id,
        "user_id": new_credit.user_id,
        "customer_id": new_credit.customer_id,
        "customer_name": customer.name,
        "amount": new_credit.amount,
        "description": new_credit.description,
        "date": new_credit.date,
        "created_at": new_credit.created_at
    }

@router.delete("/{credit_id}")
def delete_credit(
    credit_id: int, 
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    credit = db.query(Credit).filter(Credit.credit_id == credit_id).first()
    
    if not credit:
        raise HTTPException(status_code=404, detail="Credit not found")
    
    if credit.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this credit")
    
    db.delete(credit)
    db.commit()
    
    return {"message": "Credit deleted successfully"}