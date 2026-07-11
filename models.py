from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    id: str
    role: str
    name: str
    city: str
    phone: Optional[str] = None
    verification_status: str = "unverified"
    created_at: Optional[datetime] = None

class Product(BaseModel):
    id: str
    producer_id: str
    name: str
    category: str
    sector: str
    quantity: float
    unit: str
    price_etb: float
    city: str
    status: str = "active"
    created_at: Optional[datetime] = None

class Order(BaseModel):
    id: str
    buyer_id: str
    seller_id: str
    product_id: str
    quantity: float
    total_price_etb: float
    status: str = "Pending"
    payment_method: str
    created_at: Optional[datetime] = None

class Agreement(BaseModel):
    id: str
    producer_id: str
    merchant_id: str
    order_id: Optional[str] = None
    terms_json: Dict[str, Any]
    pdf_url: Optional[str] = None
    signed_at: Optional[datetime] = None

class FraudAlert(BaseModel):
    id: str
    transaction_id: str
    risk_score: float
    flags_json: List[str]
    reviewed: bool = False
    created_at: Optional[datetime] = None

class ForecastResult(BaseModel):
    product_category: str
    sector: str
    region: str
    forecast_dates: List[str]
    predicted_demand: List[float]
