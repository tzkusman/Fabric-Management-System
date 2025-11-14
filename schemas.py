from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupplierCreate(BaseModel):
    name: str
    contact: Optional[str] = None

class CustomerCreate(BaseModel):
    name: str
    contact: Optional[str] = None

class PurchaseCreate(BaseModel):
    supplier_id: int
    fabric_type: str
    fabric_code: Optional[str] = None
    composition: Optional[str] = None
    quantity_meters: float
    price_per_meter: float

class SaleCreate(BaseModel):
    customer_id: int
    fabric_type: str
    fabric_code: Optional[str] = None
    composition: Optional[str] = None
    quantity_meters: float
    price_per_meter: float
    apply_tax: Optional[bool] = True
    tax_rate: Optional[float] = 0.18

class APIPurchase(PurchaseCreate):
    pass

class APISale(SaleCreate):
    pass

# Response schemas (simple)
class SupplierOut(SupplierCreate):
    supplier_id: int

class CustomerOut(CustomerCreate):
    customer_id: int

class PurchaseOut(PurchaseCreate):
    purchase_id: int
    date: datetime
    total_cost: float

class SaleOut(SaleCreate):
    sale_id: int
    date: datetime
    apply_tax: bool
    tax: float
    total_price_with_tax: float
