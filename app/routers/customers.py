from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.get("", response_model=List[CustomerResponse])
def get_customers(user_id: int = Query(...), db: Session = Depends(get_db)):
    customers = db.query(Customer).filter(Customer.user_id == user_id).all()
    return customers

@router.post("", response_model=CustomerResponse)
def create_customer(request: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = Customer(
        user_id=request.user_id,
        name=request.name,
        phone=request.phone,
        email=request.email
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    return new_customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int, 
    request: CustomerUpdate, 
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if customer.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this customer")
    
    customer.name = request.name
    customer.phone = request.phone
    customer.email = request.email
    
    db.commit()
    db.refresh(customer)
    
    return customer

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int, 
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if customer.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this customer")
    
    db.delete(customer)
    db.commit()
    
    return {"message": "Customer deleted successfully"}