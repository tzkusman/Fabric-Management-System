from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    tax_number = Column(String, nullable=True)
    license_number = Column(String, nullable=True)
    website = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=True)

    purchases = relationship("Purchase", back_populates="supplier")

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=True)

    sales = relationship("Sale", back_populates="customer")

class Purchase(Base):
    __tablename__ = "purchases"
    purchase_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    fabric_type = Column(String, nullable=False)
    fabric_code = Column(String, nullable=True)
    composition = Column(String, nullable=True)
    quantity_meters = Column(Float, nullable=False)
    price_per_meter = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    # Payment tracking fields
    payment_method = Column(String, nullable=False, default='cash')  # 'cash', 'credit', 'bank', 'cheque'
    payment_status = Column(String, nullable=False, default='paid')  # 'paid', 'pending', 'partial'
    amount_paid = Column(Float, nullable=False, default=0.0)
    amount_due = Column(Float, nullable=False, default=0.0)
    payment_notes = Column(String, nullable=True)

    supplier = relationship("Supplier", back_populates="purchases")
    payments = relationship("PurchasePayment", back_populates="purchase", cascade="all, delete-orphan")

class Sale(Base):
    __tablename__ = "sales"
    sale_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)  # Optional for backward compatibility
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    fabric_type = Column(String, nullable=False)
    fabric_code = Column(String, nullable=True)
    composition = Column(String, nullable=True)
    quantity_meters = Column(Float, nullable=False)
    price_per_meter = Column(Float, nullable=False)
    apply_tax = Column(Boolean, nullable=False, default=True)
    tax_rate = Column(Float, nullable=True)  # Store the actual tax rate used
    tax = Column(Float, nullable=False)
    total_price_with_tax = Column(Float, nullable=False)
    
    # Payment tracking fields
    payment_method = Column(String, nullable=False, default='cash')  # 'cash' or 'credit'
    payment_status = Column(String, nullable=False, default='paid')  # 'paid', 'pending', 'partial'
    amount_paid = Column(Float, nullable=False, default=0.0)  # Amount paid so far
    amount_due = Column(Float, nullable=False, default=0.0)  # Remaining amount
    payment_notes = Column(String, nullable=True)  # Optional notes

    company = relationship("Company")
    customer = relationship("Customer", back_populates="sales")
    payments = relationship("Payment", back_populates="sale", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # 'cash', 'bank', 'cheque', 'online'
    reference_number = Column(String, nullable=True)  # Cheque number, transaction ID, etc.
    notes = Column(String, nullable=True)
    recorded_by = Column(String, nullable=True)  # Who recorded this payment
    
    sale = relationship("Sale", back_populates="payments")

class PurchasePayment(Base):
    __tablename__ = "purchase_payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.purchase_id"), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # 'cash', 'bank', 'cheque', 'online'
    reference_number = Column(String, nullable=True)  # Cheque number, transaction ID, etc.
    notes = Column(String, nullable=True)
    recorded_by = Column(String, nullable=True)  # Who recorded this payment
    
    purchase = relationship("Purchase", back_populates="payments")

class BankStatement(Base):
    __tablename__ = "bank_statements"
    statement_id = Column(Integer, primary_key=True, index=True)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    transaction_type = Column(String, nullable=False)  # 'credit' (money in) or 'debit' (money out)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)  # e.g., "Sale Payment from Customer X", "Payment to Supplier Y"
    bank_account = Column(String, nullable=True)  # Account number or name
    reference_number = Column(String, nullable=True)  # Cheque number, transaction ID, transfer reference
    related_sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=True)  # Link to sale payment
    related_purchase_id = Column(Integer, ForeignKey("purchases.purchase_id"), nullable=True)  # Link to purchase payment
    payment_method = Column(String, nullable=True)  # 'bank', 'cheque', 'online', 'transfer'
    status = Column(String, nullable=False, default='pending')  # 'pending', 'cleared', 'failed'
    reconciliation_notes = Column(String, nullable=True)
    recorded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sale = relationship("Sale")
    purchase = relationship("Purchase")

