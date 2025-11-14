from sqlalchemy.orm import Session
import models
from datetime import datetime
from sqlalchemy import func

# Default tax rate removed as it's now dynamic
# Companies
def create_company(db: Session, company_name: str, address: str = None, phone: str = None, 
                  email: str = None, tax_number: str = None, license_number: str = None, website: str = None):
    company = models.Company(
        company_name=company_name,
        address=address,
        phone=phone,
        email=email,
        tax_number=tax_number,
        license_number=license_number,
        website=website
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def get_companies(db: Session):
    return db.query(models.Company).all()

def get_company_by_id(db: Session, company_id: int):
    return db.query(models.Company).filter(models.Company.company_id == company_id).first()

# Suppliers
def create_supplier(db: Session, name: str, contact: str | None = None):
    s = models.Supplier(name=name, contact=contact)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

# Customers
def create_customer(db: Session, name: str, contact: str | None = None):
    c = models.Customer(name=name, contact=contact)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

# Purchase
def create_purchase(db: Session, supplier_id: int, fabric_type: str, quantity_meters: float, price_per_meter: float, 
                   fabric_code: str | None = None, composition: str | None = None, payment_method: str = 'cash', 
                   payment_status: str = 'paid', amount_paid: float = None):
    total_cost = quantity_meters * price_per_meter
    
    # Calculate payment amounts
    if payment_status == 'paid':
        actual_amount_paid = total_cost
        actual_amount_due = 0.0
    elif payment_status == 'pending':
        actual_amount_paid = 0.0
        actual_amount_due = total_cost
    elif payment_status == 'partial':
        if amount_paid is None or amount_paid <= 0:
            raise ValueError("For partial payment, amount_paid must be provided and greater than 0")
        if amount_paid >= total_cost:
            raise ValueError("For partial payment, amount_paid must be less than total cost")
        actual_amount_paid = amount_paid
        actual_amount_due = total_cost - amount_paid
    else:
        raise ValueError(f"Invalid payment_status: {payment_status}")
    
    p = models.Purchase(
        supplier_id=supplier_id,
        fabric_type=fabric_type,
        fabric_code=fabric_code,
        composition=composition,
        quantity_meters=quantity_meters,
        price_per_meter=price_per_meter,
        total_cost=total_cost,
        payment_method=payment_method,
        payment_status=payment_status,
        amount_paid=actual_amount_paid,
        amount_due=actual_amount_due
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

# Sale
def create_sale(db: Session, company_id: int, customer_id: int, fabric_type: str, quantity_meters: float, 
                price_per_meter: float, fabric_code: str | None = None, composition: str | None = None, 
                apply_tax: bool = True, tax_rate: float = 0.18, payment_method: str = 'cash', 
                payment_status: str = 'paid', amount_paid: float = None):
    # stock check: sum purchases - sum sales for this fabric_type (+ optional fabric_code/composition)
    purchase_filter = [models.Purchase.fabric_type==fabric_type]
    sale_filter = [models.Sale.fabric_type==fabric_type]
    if fabric_code:
        purchase_filter.append(models.Purchase.fabric_code==fabric_code)
        sale_filter.append(models.Sale.fabric_code==fabric_code)
    if composition:
        purchase_filter.append(models.Purchase.composition==composition)
        sale_filter.append(models.Sale.composition==composition)
    tp = db.query(func.coalesce(func.sum(models.Purchase.quantity_meters), 0)).filter(*purchase_filter).scalar() or 0
    ts = db.query(func.coalesce(func.sum(models.Sale.quantity_meters), 0)).filter(*sale_filter).scalar() or 0
    available = float(tp - ts)
    if quantity_meters > available:
        raise ValueError(f"Insufficient stock for {fabric_type}. Available: {available}")

    subtotal = quantity_meters * price_per_meter
    tax = round(subtotal * tax_rate, 2) if apply_tax else 0.0
    total_with_tax = subtotal if not apply_tax else round(subtotal + tax, 2)
    actual_tax_rate = tax_rate if apply_tax else 0.0
    
    # Calculate payment amounts
    if amount_paid is None:
        amount_paid = total_with_tax if payment_status == 'paid' else 0.0
    amount_due = total_with_tax - amount_paid
    
    # Determine payment status
    if amount_paid >= total_with_tax:
        payment_status = 'paid'
        amount_due = 0.0
    elif amount_paid > 0:
        payment_status = 'partial'
    else:
        payment_status = 'pending'
    
    s = models.Sale(
        company_id=company_id,
        customer_id=customer_id,
        fabric_type=fabric_type,
        quantity_meters=quantity_meters,
        fabric_code=fabric_code,
        composition=composition,
        price_per_meter=price_per_meter,
        apply_tax=apply_tax,
        tax_rate=actual_tax_rate,
        tax=tax,
        total_price_with_tax=total_with_tax,
        payment_method=payment_method,
        payment_status=payment_status,
        amount_paid=amount_paid,
        amount_due=amount_due,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

# Queries
from sqlalchemy import func

def get_purchases(db: Session):
    return db.query(models.Purchase).order_by(models.Purchase.date.desc()).all()

def get_sales(db: Session):
    return db.query(models.Sale).order_by(models.Sale.date.desc()).all()

def get_stock_summary(db: Session, q: str | None = None):
    # returns list of dicts grouped by (fabric_type, fabric_code, composition)
    purchases_q = db.query(models.Purchase.fabric_type, models.Purchase.fabric_code, models.Purchase.composition).distinct()
    sales_q = db.query(models.Sale.fabric_type, models.Sale.fabric_code, models.Sale.composition).distinct()

    types = set([(r[0], r[1], r[2]) for r in purchases_q]) | set([(r[0], r[1], r[2]) for r in sales_q])

    result = []
    for t_type, t_code, t_comp in types:
        # optional search filter
        if q:
            if q.lower() not in (str(t_type or '').lower() + ' ' + str(t_code or '').lower() + ' ' + str(t_comp or '').lower()):
                continue

        # totals
        tp = db.query(func.coalesce(func.sum(models.Purchase.quantity_meters), 0)).filter(models.Purchase.fabric_type==t_type, models.Purchase.fabric_code==t_code).scalar() or 0
        ts = db.query(func.coalesce(func.sum(models.Sale.quantity_meters), 0)).filter(models.Sale.fabric_type==t_type, models.Sale.fabric_code==t_code).scalar() or 0

        # FIFO valuation: iterate purchases oldest->newest, subtract sold quantities to find remaining lots
        purchases = db.query(models.Purchase).filter(models.Purchase.fabric_type==t_type, models.Purchase.fabric_code==t_code).order_by(models.Purchase.date.asc()).all()
        total_sold = float(ts)
        valuation = 0.0
        remaining = 0.0

        # allocate sold against purchase lots
        for p in purchases:
            lot_qty = float(p.quantity_meters)
            if total_sold >= lot_qty:
                # this lot fully consumed
                total_sold -= lot_qty
                lot_remaining = 0.0
            else:
                lot_remaining = lot_qty - total_sold
                total_sold = 0.0
            if lot_remaining > 0:
                valuation += lot_remaining * float(p.price_per_meter)
                remaining += lot_remaining

        balance = float(tp - ts)
        avg_cost = (valuation / remaining) if remaining > 0 else 0.0

        result.append({
            "fabric_type": t_type,
            "fabric_code": t_code,
            "composition": t_comp,
            "total_purchased": float(tp),
            "total_sold": float(ts),
            "balance_in_meters": balance,
            "avg_cost_per_meter": round(avg_cost, 2),
            "stock_valuation": round(valuation, 2),
        })
    return result

# Profit/Loss (simple): total sales (net) - total purchases
def get_profit_loss(db: Session):
    total_purchased_cost = db.query(func.coalesce(func.sum(models.Purchase.total_cost), 0)).scalar() or 0
    total_sales_revenue = db.query(func.coalesce(func.sum(models.Sale.total_price_with_tax), 0)).scalar() or 0
    profit = float(total_sales_revenue - total_purchased_cost)
    return {"total_purchased_cost": float(total_purchased_cost), "total_sales_revenue": float(total_sales_revenue), "profit": profit}


def get_available_fabrics(db: Session):
    # return fabrics with positive balance
    stock = get_stock_summary(db)
    return [s for s in stock if s['balance_in_meters'] > 0]

# Ledger functions with advanced filtering
def get_purchase_ledger(db: Session, supplier_id: int = None, fabric_type: str = None, 
                        fabric_code: str = None, date_from: datetime = None, 
                        date_to: datetime = None, search_query: str = None):
    """
    Get purchase ledger with advanced filters
    Returns list of purchases with calculated totals
    """
    query = db.query(models.Purchase).join(models.Supplier)
    
    # Apply filters
    if supplier_id:
        query = query.filter(models.Purchase.supplier_id == supplier_id)
    
    if fabric_type:
        query = query.filter(models.Purchase.fabric_type.ilike(f'%{fabric_type}%'))
    
    if fabric_code:
        query = query.filter(models.Purchase.fabric_code.ilike(f'%{fabric_code}%'))
    
    if date_from:
        query = query.filter(models.Purchase.date >= date_from)
    
    if date_to:
        # Include the entire end date
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.Purchase.date < date_to_end)
    
    if search_query:
        # Search across multiple fields
        search_pattern = f'%{search_query}%'
        query = query.filter(
            (models.Purchase.fabric_type.ilike(search_pattern)) |
            (models.Purchase.fabric_code.ilike(search_pattern)) |
            (models.Purchase.composition.ilike(search_pattern)) |
            (models.Supplier.name.ilike(search_pattern))
        )
    
    purchases = query.order_by(models.Purchase.date.desc()).all()
    
    # Calculate totals
    total_quantity = sum(p.quantity_meters for p in purchases)
    total_amount = sum(p.total_cost for p in purchases)
    
    return {
        'purchases': purchases,
        'total_quantity': round(total_quantity, 2),
        'total_amount': round(total_amount, 2),
        'count': len(purchases)
    }

def get_sale_ledger(db: Session, customer_id: int = None, company_id: int = None,
                   fabric_type: str = None, fabric_code: str = None, 
                   date_from: datetime = None, date_to: datetime = None, 
                   search_query: str = None, apply_tax_filter: bool = None):
    """
    Get sale ledger with advanced filters
    Returns list of sales with calculated totals
    """
    query = db.query(models.Sale).join(models.Customer)
    
    # Apply filters
    if customer_id:
        query = query.filter(models.Sale.customer_id == customer_id)
    
    if company_id:
        query = query.filter(models.Sale.company_id == company_id)
    
    if fabric_type:
        query = query.filter(models.Sale.fabric_type.ilike(f'%{fabric_type}%'))
    
    if fabric_code:
        query = query.filter(models.Sale.fabric_code.ilike(f'%{fabric_code}%'))
    
    if date_from:
        query = query.filter(models.Sale.date >= date_from)
    
    if date_to:
        # Include the entire end date
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.Sale.date < date_to_end)
    
    if apply_tax_filter is not None:
        query = query.filter(models.Sale.apply_tax == apply_tax_filter)
    
    if search_query:
        # Search across multiple fields
        search_pattern = f'%{search_query}%'
        query = query.filter(
            (models.Sale.fabric_type.ilike(search_pattern)) |
            (models.Sale.fabric_code.ilike(search_pattern)) |
            (models.Sale.composition.ilike(search_pattern)) |
            (models.Customer.name.ilike(search_pattern))
        )
    
    sales = query.order_by(models.Sale.date.desc()).all()
    
    # Calculate totals
    total_quantity = sum(s.quantity_meters for s in sales)
    subtotal = sum(s.quantity_meters * s.price_per_meter for s in sales)
    total_tax = sum(s.tax for s in sales)
    total_amount = sum(s.total_price_with_tax for s in sales)
    
    return {
        'sales': sales,
        'total_quantity': round(total_quantity, 2),
        'subtotal': round(subtotal, 2),
        'total_tax': round(total_tax, 2),
        'total_amount': round(total_amount, 2),
        'count': len(sales)
    }

def get_customer_ledger_summary(db: Session, date_from: datetime = None, date_to: datetime = None):
    """
    Get summary of sales grouped by customer for ledger overview
    """
    query = db.query(
        models.Customer.customer_id,
        models.Customer.name,
        models.Customer.contact,
        func.count(models.Sale.sale_id).label('transaction_count'),
        func.sum(models.Sale.quantity_meters).label('total_quantity'),
        func.sum(models.Sale.total_price_with_tax).label('total_amount')
    ).join(models.Sale).group_by(models.Customer.customer_id)
    
    if date_from:
        query = query.filter(models.Sale.date >= date_from)
    
    if date_to:
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.Sale.date < date_to_end)
    
    results = query.all()
    
    return [{
        'customer_id': r.customer_id,
        'customer_name': r.name,
        'contact': r.contact,
        'transaction_count': r.transaction_count,
        'total_quantity': round(float(r.total_quantity or 0), 2),
        'total_amount': round(float(r.total_amount or 0), 2)
    } for r in results]

def get_supplier_ledger_summary(db: Session, date_from: datetime = None, date_to: datetime = None):
    """
    Get summary of purchases grouped by supplier for ledger overview
    """
    query = db.query(
        models.Supplier.supplier_id,
        models.Supplier.name,
        models.Supplier.contact,
        func.count(models.Purchase.purchase_id).label('transaction_count'),
        func.sum(models.Purchase.quantity_meters).label('total_quantity'),
        func.sum(models.Purchase.total_cost).label('total_amount')
    ).join(models.Purchase).group_by(models.Supplier.supplier_id)
    
    if date_from:
        query = query.filter(models.Purchase.date >= date_from)
    
    if date_to:
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.Purchase.date < date_to_end)
    
    results = query.all()
    
    return [{
        'supplier_id': r.supplier_id,
        'supplier_name': r.name,
        'contact': r.contact,
        'transaction_count': r.transaction_count,
        'total_quantity': round(float(r.total_quantity or 0), 2),
        'total_amount': round(float(r.total_amount or 0), 2)
    } for r in results]

# Payment management functions
def add_payment(db: Session, sale_id: int, amount: float, payment_method: str = 'cash', 
                reference_number: str = None, notes: str = None, recorded_by: str = None):
    """
    Record a payment against a sale
    """
    sale = db.query(models.Sale).filter(models.Sale.sale_id == sale_id).first()
    if not sale:
        raise ValueError(f"Sale {sale_id} not found")
    
    if amount <= 0:
        raise ValueError("Payment amount must be greater than 0")
    
    if amount > sale.amount_due:
        raise ValueError(f"Payment amount ({amount}) exceeds due amount ({sale.amount_due})")
    
    # Create payment record
    payment = models.Payment(
        sale_id=sale_id,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number,
        notes=notes,
        recorded_by=recorded_by
    )
    db.add(payment)
    
    # Update sale payment status
    sale.amount_paid += amount
    sale.amount_due -= amount
    
    if sale.amount_due <= 0:
        sale.payment_status = 'paid'
        sale.amount_due = 0.0
    else:
        sale.payment_status = 'partial'
    
    db.commit()
    db.refresh(sale)
    db.refresh(payment)
    return payment

def get_payments_for_sale(db: Session, sale_id: int):
    """
    Get all payment records for a sale
    """
    return db.query(models.Payment).filter(models.Payment.sale_id == sale_id).order_by(models.Payment.payment_date.desc()).all()

def get_pending_payments(db: Session, customer_id: int = None):
    """
    Get all sales with pending or partial payments
    """
    query = db.query(models.Sale).filter(models.Sale.payment_status.in_(['pending', 'partial']))
    
    if customer_id:
        query = query.filter(models.Sale.customer_id == customer_id)
    
    return query.order_by(models.Sale.date.desc()).all()

def get_customer_credit_summary(db: Session, date_from: datetime = None, date_to: datetime = None):
    """
    Get summary of customers with outstanding credit
    """
    query = db.query(
        models.Customer.customer_id,
        models.Customer.name,
        models.Customer.contact,
        func.count(models.Sale.sale_id).label('pending_count'),
        func.sum(models.Sale.amount_due).label('total_due'),
        func.sum(models.Sale.total_price_with_tax).label('total_sales')
    ).join(models.Sale).filter(models.Sale.payment_status.in_(['pending', 'partial'])).group_by(models.Customer.customer_id)
    
    if date_from:
        query = query.filter(models.Sale.date >= date_from)
    
    if date_to:
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.Sale.date < date_to_end)
    
    results = query.all()
    
    return [{
        'customer_id': r.customer_id,
        'customer_name': r.name,
        'contact': r.contact,
        'pending_count': r.pending_count,
        'total_due': round(float(r.total_due or 0), 2),
        'total_sales': round(float(r.total_sales or 0), 2)
    } for r in results]

def get_payment_history(db: Session, customer_id: int = None, date_from: datetime = None, date_to: datetime = None):
    """
    Get payment history with customer details
    """
    query = db.query(models.Payment).join(models.Sale).join(models.Customer)
    
    if customer_id:
        query = query.filter(models.Customer.customer_id == customer_id)
    
    if date_from:
        query = query.filter(models.Payment.payment_date >= date_from)
    
    if date_to:
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.Payment.payment_date < date_to_end)
    
    return query.order_by(models.Payment.payment_date.desc()).all()

# Purchase Payment management functions
def add_purchase_payment(db: Session, purchase_id: int, amount: float, payment_method: str = 'cash', 
                        reference_number: str = None, notes: str = None, recorded_by: str = None):
    """
    Record a payment against a purchase
    """
    purchase = db.query(models.Purchase).filter(models.Purchase.purchase_id == purchase_id).first()
    if not purchase:
        raise ValueError(f"Purchase {purchase_id} not found")
    
    if amount <= 0:
        raise ValueError("Payment amount must be greater than 0")
    
    if amount > purchase.amount_due:
        raise ValueError(f"Payment amount ({amount}) exceeds due amount ({purchase.amount_due})")
    
    # Create payment record
    payment = models.PurchasePayment(
        purchase_id=purchase_id,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number,
        notes=notes,
        recorded_by=recorded_by
    )
    db.add(payment)
    
    # Update purchase payment status
    purchase.amount_paid += amount
    purchase.amount_due -= amount
    
    if purchase.amount_due <= 0:
        purchase.payment_status = 'paid'
        purchase.amount_due = 0.0
    else:
        purchase.payment_status = 'partial'
    
    db.commit()
    db.refresh(purchase)
    db.refresh(payment)
    return payment

def get_payments_for_purchase(db: Session, purchase_id: int):
    """
    Get all payment records for a purchase
    """
    return db.query(models.PurchasePayment).filter(models.PurchasePayment.purchase_id == purchase_id).order_by(models.PurchasePayment.payment_date.desc()).all()

def get_pending_purchase_payments(db: Session, supplier_id: int = None):
    """
    Get all purchases with pending or partial payments
    """
    query = db.query(models.Purchase).filter(models.Purchase.payment_status.in_(['pending', 'partial']))
    
    if supplier_id:
        query = query.filter(models.Purchase.supplier_id == supplier_id)
    
    return query.order_by(models.Purchase.date.desc()).all()

def get_supplier_credit_summary(db: Session, date_from: datetime = None, date_to: datetime = None):
    """
    Get summary of suppliers with outstanding credit (amounts we owe)
    """
    query = db.query(
        models.Supplier.supplier_id,
        models.Supplier.name,
        models.Supplier.contact,
        func.count(models.Purchase.purchase_id).label('pending_count'),
        func.sum(models.Purchase.amount_due).label('total_due'),
        func.sum(models.Purchase.total_cost).label('total_purchases')
    ).join(models.Purchase).filter(models.Purchase.payment_status.in_(['pending', 'partial'])).group_by(models.Supplier.supplier_id)
    
    if date_from:
        query = query.filter(models.Purchase.date >= date_from)
    
    if date_to:
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.Purchase.date < date_to_end)
    
    results = query.all()
    
    return [{
        'supplier_id': r.supplier_id,
        'supplier_name': r.name,
        'contact': r.contact,
        'pending_count': r.pending_count,
        'total_due': round(float(r.total_due or 0), 2),
        'total_purchases': round(float(r.total_purchases or 0), 2)
    } for r in results]

def get_purchase_payment_history(db: Session, supplier_id: int = None, date_from: datetime = None, date_to: datetime = None):
    """
    Get purchase payment history with supplier details
    """
    query = db.query(models.PurchasePayment).join(models.Purchase).join(models.Supplier)
    
    if supplier_id:
        query = query.filter(models.Supplier.supplier_id == supplier_id)
    
    if date_from:
        query = query.filter(models.PurchasePayment.payment_date >= date_from)
    
    if date_to:
        from datetime import timedelta
        date_to_end = date_to + timedelta(days=1)
        query = query.filter(models.PurchasePayment.payment_date < date_to_end)
    
    return query.order_by(models.PurchasePayment.payment_date.desc()).all()
