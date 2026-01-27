from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from core.config import CORS_ORIGINS
from routers import auth, customers, credits, payments, dashboard, ledger

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ShopKhata API",
    description="Digital Credit Management System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(credits.router)
app.include_router(payments.router)
app.include_router(dashboard.router)
app.include_router(ledger.router)

@app.get("/")
def root():
    return {
        "message": "ShopKhata API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}