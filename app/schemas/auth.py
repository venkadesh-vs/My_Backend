from pydantic import BaseModel

class RegisterRequest(BaseModel):
    shop_name: str
    owner_name: str
    email: str
    phone: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    shop_name: str
    owner_name: str
    email: str
    phone: str
    
class Config:
    from_attributes = True