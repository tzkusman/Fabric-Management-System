from fastapi import FastAPI, Request, Form, Depends, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, Response, FileResponse, RedirectResponse
from pydantic import BaseModel
import schemas
import shutil
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

import database, models, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Resolve templates directory for both portable and development environments
def get_templates_dir():
    """Get templates directory path, handling PyInstaller environment"""
    import sys
    # Check if running as PyInstaller executable
    if getattr(sys, 'frozen', False):
        # Running as executable - templates are in the exe's directory
        app_root = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_root = os.path.dirname(os.path.abspath(__file__))
    
    templates_path = os.path.join(app_root, 'templates')
    if not os.path.exists(templates_path):
        # Fallback to relative path
        templates_path = 'templates'
    return templates_path

templates = Jinja2Templates(directory=get_templates_dir())
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
import time
# provide a callable to templates for cache-busting
templates.env.globals['now'] = lambda: int(time.time())

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/database", response_class=HTMLResponse)
def database_operations(request: Request):
    return templates.TemplateResponse("database_operations.html", {"request": request})

# Company Registration
@app.get('/register_company', response_class=HTMLResponse)
def register_company_form(request: Request, db: Session = Depends(get_db)):
    companies = crud.get_companies(db)
    return templates.TemplateResponse('register_company.html', {"request": request, "companies": companies})

@app.post('/register_company')
async def register_company_post(
    request: Request,
    company_name: str = Form(...),
    address: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    tax_number: str = Form(None),
    license_number: str = Form(None),
    website: str = Form(None),
    db: Session = Depends(get_db)
):
    company = crud.create_company(
        db, 
        company_name=company_name,
        address=address,
        phone=phone,
        email=email,
        tax_number=tax_number,
        license_number=license_number,
        website=website
    )
    companies = crud.get_companies(db)
    return templates.TemplateResponse('register_company.html', {
        "request": request, 
        "message": f"Company '{company.company_name}' registered successfully!", 
        "companies": companies
    })

@app.post('/company/delete')
def delete_company(company_id: int = Form(...), db: Session = Depends(get_db)):
    # First check if company has any sales
    sale_count = db.query(models.Sale).filter(models.Sale.company_id == company_id).count()
    if sale_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete company: Found {sale_count} related sale records. Please delete the sales first."
        )
    
    company = db.query(models.Company).filter(models.Company.company_id == company_id).first()
    if company:
        db.delete(company)
        db.commit()
        return {"ok": True, "message": f"Company {company.company_name} deleted successfully"}
    raise HTTPException(status_code=404, detail="Company not found")

# Supplier create
@app.get('/add_supplier', response_class=HTMLResponse)
def add_supplier_form(request: Request):
    suppliers = []
    db = next(get_db())
    try:
        suppliers = db.query(models.Supplier).all()
    finally:
        db.close()
    return templates.TemplateResponse('add_supplier.html', {"request": request, "suppliers": suppliers})

@app.post('/add_supplier')
async def add_supplier(request: Request, name: str = Form(...), contact: str = Form(None), db: Session = Depends(get_db)):
    s = crud.create_supplier(db, name=name, contact=contact)
    # re-render form with message
    return templates.TemplateResponse('add_supplier.html', {"request": request, "message": f"Supplier {s.name} added."})

# Customer create
@app.get('/add_customer', response_class=HTMLResponse)
def add_customer_form(request: Request):
    customers = []
    db = next(get_db())
    try:
        customers = db.query(models.Customer).all()
    finally:
        db.close()
    return templates.TemplateResponse('add_customer.html', {"request": request, "customers": customers})

@app.post('/add_customer')
async def add_customer(request: Request, name: str = Form(...), contact: str = Form(None), db: Session = Depends(get_db)):
    c = crud.create_customer(db, name=name, contact=contact)
    return templates.TemplateResponse('add_customer.html', {"request": request, "message": f"Customer {c.name} added."})

# Purchase
@app.get('/add_purchase', response_class=HTMLResponse)
def add_purchase_get(request: Request, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).all()
    return templates.TemplateResponse('add_purchase.html', {"request": request, "suppliers": suppliers})

@app.post('/add_purchase')
async def add_purchase_post(
    request: Request,
    supplier_id: int = Form(...),
    fabric_type: str = Form(...),
    quantity_meters: float = Form(...),
    price_per_meter: float = Form(...),
    fabric_code: str | None = Form(None),
    composition: str | None = Form(None),
    payment_method: str = Form('cash'),
    payment_status: str = Form('paid'),
    amount_paid: float | None = Form(None),
    db: Session = Depends(get_db),
):
    # persist purchase including fabric_code, composition, and payment details
    p = crud.create_purchase(
        db, 
        supplier_id=supplier_id, 
        fabric_type=fabric_type, 
        quantity_meters=quantity_meters, 
        price_per_meter=price_per_meter, 
        fabric_code=fabric_code, 
        composition=composition,
        payment_method=payment_method,
        payment_status=payment_status,
        amount_paid=amount_paid
    )
    suppliers = db.query(models.Supplier).all()
    return templates.TemplateResponse('add_purchase.html', {"request": request, "message": f"Purchase recorded (id={p.purchase_id}).", "suppliers": suppliers})

# Sale
@app.get('/add_sale', response_class=HTMLResponse)
def add_sale_get(request: Request, db: Session = Depends(get_db)):
    companies = crud.get_companies(db)
    customers = db.query(models.Customer).all()
    fabrics = crud.get_available_fabrics(db)
    return templates.TemplateResponse('add_sale.html', {"request": request, "companies": companies, "customers": customers, "fabrics": fabrics})


@app.post('/supplier/delete')
def delete_supplier(supplier_id: int = Form(...), db: Session = Depends(get_db)):
    # First check if supplier has any purchases
    purchase_count = db.query(models.Purchase).filter(models.Purchase.supplier_id == supplier_id).count()
    if purchase_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete supplier: Found {purchase_count} related purchase records. Please delete the purchases first."
        )
    
    s = db.query(models.Supplier).filter(models.Supplier.supplier_id==supplier_id).first()
    if s:
        db.delete(s)
        db.commit()
        return {"ok": True, "message": f"Supplier {s.name} deleted successfully"}
    raise HTTPException(status_code=404, detail="Supplier not found")


@app.post('/customer/delete')
def delete_customer(customer_id: int = Form(...), db: Session = Depends(get_db)):
    # First check if customer has any sales
    sale_count = db.query(models.Sale).filter(models.Sale.customer_id == customer_id).count()
    if sale_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete customer: Found {sale_count} related sale records. Please delete the sales first."
        )
    
    c = db.query(models.Customer).filter(models.Customer.customer_id==customer_id).first()
    if c:
        db.delete(c)
        db.commit()
        return {"ok": True, "message": f"Customer {c.name} deleted successfully"}
    raise HTTPException(status_code=404, detail="Customer not found")

@app.post('/add_sale')
async def add_sale_post(
    request: Request,
    company_id: int = Form(...),
    customer_id: int = Form(...),
    fabric_type: str = Form(...),
    quantity_meters: float = Form(...),
    price_per_meter: float = Form(...),
    fabric_code: str | None = Form(None),
    composition: str | None = Form(None),
    apply_tax: bool = Form(False),
    tax_rate: float = Form(18.0),
    payment_method: str = Form('cash'),
    payment_status: str = Form('paid'),
    amount_paid: float = Form(None),
    db: Session = Depends(get_db),
):
    # If fabric_type field contains encoded value from select (type||code||composition), parse it
    if '||' in fabric_type:
        parts = fabric_type.split('||')
        fabric_type = parts[0]
        fabric_code = parts[1] if len(parts) > 1 and parts[1] != '' else None
        composition = parts[2] if len(parts) > 2 and parts[2] != '' else None

    # Basic stock check (respect fabric_code when present)
    stock = crud.get_stock_summary(db)
    bal = 0
    for s in stock:
        if s['fabric_type'] == fabric_type and (fabric_code is None or s['fabric_code'] == fabric_code):
            bal = s['balance_in_meters']
    if quantity_meters > bal:
        raise HTTPException(status_code=400, detail=f"Insufficient stock for {fabric_type}. Available: {bal}")
    try:
        # Convert tax_rate from percentage to decimal
        tax_rate_decimal = tax_rate / 100 if apply_tax else 0
        s = crud.create_sale(db, company_id=company_id, customer_id=customer_id, fabric_type=fabric_type, 
                            quantity_meters=quantity_meters, price_per_meter=price_per_meter, 
                            fabric_code=fabric_code, composition=composition, apply_tax=apply_tax, 
                            tax_rate=tax_rate_decimal, payment_method=payment_method, 
                            payment_status=payment_status, amount_paid=amount_paid)
    except ValueError as e:
        companies = crud.get_companies(db)
        customers = db.query(models.Customer).all()
        fabrics = crud.get_available_fabrics(db)
        return templates.TemplateResponse('add_sale.html', {"request": request, "error": str(e), "companies": companies, "customers": customers, "fabrics": fabrics})
    if fabric_code or composition:
        s.fabric_code = fabric_code
        s.composition = composition
        db.add(s); db.commit(); db.refresh(s)
    companies = crud.get_companies(db)
    customers = db.query(models.Customer).all()
    fabrics = crud.get_available_fabrics(db)
    return templates.TemplateResponse('add_sale.html', {"request": request, "message": f"Sale recorded (id={s.sale_id}). Payment status: {s.payment_status}", "companies": companies, "customers": customers, "fabrics": fabrics})

# Listings / reports
@app.get('/purchases', response_class=HTMLResponse)
def purchases_list(request: Request, db: Session = Depends(get_db)):
    purchases = db.query(models.Purchase).order_by(models.Purchase.date.desc()).all()
    return templates.TemplateResponse('purchases.html', {"request": request, "purchases": purchases})

@app.get('/sales', response_class=HTMLResponse)
def sales_list(request: Request, db: Session = Depends(get_db)):
    sales = db.query(models.Sale).order_by(models.Sale.date.desc()).all()
    return templates.TemplateResponse('sales.html', {"request": request, "sales": sales})

@app.get('/stock', response_class=HTMLResponse)
def stock_summary(request: Request, db: Session = Depends(get_db)):
    q = request.query_params.get('q')
    stock = crud.get_stock_summary(db, q=q)
    return templates.TemplateResponse('stock.html', {"request": request, "stock": stock})


@app.get('/fabrics', response_class=HTMLResponse)
def fabrics_list(request: Request, db: Session = Depends(get_db)):
    fabrics = []
    # gather distinct fabric_type/code/composition
    rows = db.query(models.Purchase.fabric_type, models.Purchase.fabric_code, models.Purchase.composition).distinct().all()
    for r in rows:
        fabrics.append({"fabric_type": r[0], "fabric_code": r[1], "composition": r[2]})
    return templates.TemplateResponse('fabrics.html', {"request": request, "fabrics": fabrics})


@app.get('/api/fabrics')
def api_fabrics(q: str | None = None, db: Session = Depends(get_db)):
    rows = db.query(models.Purchase.fabric_type, models.Purchase.fabric_code, models.Purchase.composition).distinct()
    out = []
    for r in rows:
        text = (str(r[0] or '') + ' ' + str(r[1] or '') + ' ' + str(r[2] or '')).lower()
        if not q or q.lower() in text:
            out.append({"fabric_type": r[0], "fabric_code": r[1], "composition": r[2]})
    return out


@app.get('/profit', response_class=HTMLResponse)
def profit_report(request: Request, db: Session = Depends(get_db)):
    data = crud.get_profit_loss(db)
    return templates.TemplateResponse('profit.html', {"request": request, "data": data})

# Ledger routes
@app.get('/ledger/purchases', response_class=HTMLResponse)
def purchase_ledger(request: Request, db: Session = Depends(get_db)):
    # Get all suppliers and companies for filters
    suppliers = db.query(models.Supplier).all()
    companies = crud.get_companies(db)
    
    # Get filter parameters
    supplier_id = request.query_params.get('supplier_id')
    fabric_type = request.query_params.get('fabric_type')
    fabric_code = request.query_params.get('fabric_code')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    search_query = request.query_params.get('search')
    
    # Convert dates
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    # Convert supplier_id to int if present
    supplier_id_int = int(supplier_id) if supplier_id else None
    
    # Get ledger data
    ledger_data = crud.get_purchase_ledger(
        db, 
        supplier_id=supplier_id_int,
        fabric_type=fabric_type if fabric_type else None,
        fabric_code=fabric_code if fabric_code else None,
        date_from=date_from_obj,
        date_to=date_to_obj,
        search_query=search_query if search_query else None
    )
    
    return templates.TemplateResponse('ledger_purchases.html', {
        "request": request, 
        "ledger": ledger_data,
        "suppliers": suppliers,
        "companies": companies,
        "filters": {
            'supplier_id': supplier_id,
            'fabric_type': fabric_type,
            'fabric_code': fabric_code,
            'date_from': date_from,
            'date_to': date_to,
            'search': search_query
        }
    })

@app.get('/ledger/sales', response_class=HTMLResponse)
def sale_ledger(request: Request, db: Session = Depends(get_db)):
    # Get all customers and companies for filters
    customers = db.query(models.Customer).all()
    companies = crud.get_companies(db)
    
    # Get filter parameters
    customer_id = request.query_params.get('customer_id')
    company_id = request.query_params.get('company_id')
    fabric_type = request.query_params.get('fabric_type')
    fabric_code = request.query_params.get('fabric_code')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    search_query = request.query_params.get('search')
    apply_tax_filter = request.query_params.get('apply_tax')
    
    # Convert dates
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    # Convert IDs to int if present
    customer_id_int = int(customer_id) if customer_id else None
    company_id_int = int(company_id) if company_id else None
    
    # Convert tax filter
    tax_filter = None
    if apply_tax_filter == 'yes':
        tax_filter = True
    elif apply_tax_filter == 'no':
        tax_filter = False
    
    # Get ledger data
    ledger_data = crud.get_sale_ledger(
        db,
        customer_id=customer_id_int,
        company_id=company_id_int,
        fabric_type=fabric_type if fabric_type else None,
        fabric_code=fabric_code if fabric_code else None,
        date_from=date_from_obj,
        date_to=date_to_obj,
        search_query=search_query if search_query else None,
        apply_tax_filter=tax_filter
    )
    
    return templates.TemplateResponse('ledger_sales.html', {
        "request": request,
        "ledger": ledger_data,
        "customers": customers,
        "companies": companies,
        "filters": {
            'customer_id': customer_id,
            'company_id': company_id,
            'fabric_type': fabric_type,
            'fabric_code': fabric_code,
            'date_from': date_from,
            'date_to': date_to,
            'search': search_query,
            'apply_tax': apply_tax_filter
        }
    })

@app.get('/ledger/customer-summary', response_class=HTMLResponse)
def customer_ledger_summary(request: Request, db: Session = Depends(get_db)):
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    summary_data = crud.get_customer_ledger_summary(db, date_from=date_from_obj, date_to=date_to_obj)
    
    return templates.TemplateResponse('ledger_customer_summary.html', {
        "request": request,
        "summary": summary_data,
        "filters": {
            'date_from': date_from,
            'date_to': date_to
        }
    })

@app.get('/ledger/supplier-summary', response_class=HTMLResponse)
def supplier_ledger_summary(request: Request, db: Session = Depends(get_db)):
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    summary_data = crud.get_supplier_ledger_summary(db, date_from=date_from_obj, date_to=date_to_obj)
    
    return templates.TemplateResponse('ledger_supplier_summary.html', {
        "request": request,
        "summary": summary_data,
        "filters": {
            'date_from': date_from,
            'date_to': date_to
        }
    })

# Export ledger routes
@app.get('/export/ledger/purchases.csv')
def export_purchase_ledger(
    supplier_id: int = None,
    fabric_type: str = None,
    fabric_code: str = None,
    date_from: str = None,
    date_to: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    import csv, io
    from datetime import datetime
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    ledger_data = crud.get_purchase_ledger(
        db,
        supplier_id=supplier_id,
        fabric_type=fabric_type,
        fabric_code=fabric_code,
        date_from=date_from_obj,
        date_to=date_to_obj,
        search_query=search
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Purchase ID', 'Date', 'Supplier', 'Fabric Type', 'Fabric Code', 'Composition', 'Quantity (m)', 'Price/Meter', 'Total Cost'])
    
    for p in ledger_data['purchases']:
        writer.writerow([
            p.purchase_id,
            p.date.strftime('%Y-%m-%d %H:%M'),
            p.supplier.name,
            p.fabric_type,
            p.fabric_code or '',
            p.composition or '',
            p.quantity_meters,
            p.price_per_meter,
            p.total_cost
        ])
    
    # Add summary row
    writer.writerow([])
    writer.writerow(['TOTAL', '', '', '', '', '', ledger_data['total_quantity'], '', ledger_data['total_amount']])
    
    return Response(content=output.getvalue(), media_type='text/csv', headers={
        'Content-Disposition': f'attachment; filename=purchase_ledger_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    })

@app.get('/export/ledger/sales.csv')
def export_sale_ledger(
    customer_id: int = None,
    company_id: int = None,
    fabric_type: str = None,
    fabric_code: str = None,
    date_from: str = None,
    date_to: str = None,
    search: str = None,
    apply_tax: str = None,
    db: Session = Depends(get_db)
):
    import csv, io
    from datetime import datetime
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    tax_filter = None
    if apply_tax == 'yes':
        tax_filter = True
    elif apply_tax == 'no':
        tax_filter = False
    
    ledger_data = crud.get_sale_ledger(
        db,
        customer_id=customer_id,
        company_id=company_id,
        fabric_type=fabric_type,
        fabric_code=fabric_code,
        date_from=date_from_obj,
        date_to=date_to_obj,
        search_query=search,
        apply_tax_filter=tax_filter
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Sale ID', 'Date', 'Customer', 'Company', 'Fabric Type', 'Fabric Code', 'Composition', 'Quantity (m)', 'Price/Meter', 'Tax Applied', 'Tax Amount', 'Total'])
    
    for s in ledger_data['sales']:
        company_name = s.company.company_name if s.company else 'N/A'
        writer.writerow([
            s.sale_id,
            s.date.strftime('%Y-%m-%d %H:%M'),
            s.customer.name,
            company_name,
            s.fabric_type,
            s.fabric_code or '',
            s.composition or '',
            s.quantity_meters,
            s.price_per_meter,
            'Yes' if s.apply_tax else 'No',
            s.tax,
            s.total_price_with_tax
        ])
    
    # Add summary rows
    writer.writerow([])
    writer.writerow(['SUMMARY', '', '', '', '', '', '', ledger_data['total_quantity'], '', '', ledger_data['total_tax'], ledger_data['total_amount']])
    writer.writerow(['Subtotal', '', '', '', '', '', '', '', '', '', '', ledger_data['subtotal']])
    
    return Response(content=output.getvalue(), media_type='text/csv', headers={
        'Content-Disposition': f'attachment; filename=sale_ledger_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    })

# Payment Management Routes
@app.get('/payments/pending', response_class=HTMLResponse)
def pending_payments(request: Request, db: Session = Depends(get_db)):
    """View all pending and partial payments"""
    customer_id = request.query_params.get('customer_id')
    customer_id_int = int(customer_id) if customer_id else None
    
    pending_sales = crud.get_pending_payments(db, customer_id=customer_id_int)
    customers = db.query(models.Customer).all()
    
    # Calculate totals
    total_due = sum(s.amount_due for s in pending_sales)
    total_sales = sum(s.total_price_with_tax for s in pending_sales)
    total_paid = sum(s.amount_paid for s in pending_sales)
    
    return templates.TemplateResponse('payments_pending.html', {
        "request": request,
        "pending_sales": pending_sales,
        "customers": customers,
        "selected_customer": customer_id_int,
        "total_due": round(total_due, 2),
        "total_sales": round(total_sales, 2),
        "total_paid": round(total_paid, 2)
    })

@app.get('/payments/record/{sale_id}', response_class=HTMLResponse)
def record_payment_form(sale_id: int, request: Request, db: Session = Depends(get_db)):
    """Form to record a payment against a sale"""
    sale = db.query(models.Sale).filter(models.Sale.sale_id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    payments = crud.get_payments_for_sale(db, sale_id)
    
    return templates.TemplateResponse('record_payment.html', {
        "request": request,
        "sale": sale,
        "payments": payments
    })

@app.post('/payments/record/{sale_id}')
async def record_payment_post(
    sale_id: int,
    request: Request,
    amount: float = Form(...),
    payment_method: str = Form('cash'),
    reference_number: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Process payment recording"""
    try:
        payment = crud.add_payment(
            db,
            sale_id=sale_id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes
        )
        
        sale = db.query(models.Sale).filter(models.Sale.sale_id == sale_id).first()
        payments = crud.get_payments_for_sale(db, sale_id)
        
        return templates.TemplateResponse('record_payment.html', {
            "request": request,
            "sale": sale,
            "payments": payments,
            "message": f"Payment of Rs. {amount} recorded successfully! Remaining: Rs. {sale.amount_due}"
        })
    except ValueError as e:
        sale = db.query(models.Sale).filter(models.Sale.sale_id == sale_id).first()
        payments = crud.get_payments_for_sale(db, sale_id)
        return templates.TemplateResponse('record_payment.html', {
            "request": request,
            "sale": sale,
            "payments": payments,
            "error": str(e)
        })

@app.get('/payments/history', response_class=HTMLResponse)
def payment_history(request: Request, db: Session = Depends(get_db)):
    """View payment history"""
    customer_id = request.query_params.get('customer_id')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    customer_id_int = int(customer_id) if customer_id else None
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    payments = crud.get_payment_history(db, customer_id=customer_id_int, date_from=date_from_obj, date_to=date_to_obj)
    customers = db.query(models.Customer).all()
    
    # Calculate totals
    total_payments = sum(p.amount for p in payments)
    
    return templates.TemplateResponse('payment_history.html', {
        "request": request,
        "payments": payments,
        "customers": customers,
        "total_payments": round(total_payments, 2),
        "filters": {
            'customer_id': customer_id,
            'date_from': date_from,
            'date_to': date_to
        }
    })

@app.get('/payments/credit-summary', response_class=HTMLResponse)
def credit_summary(request: Request, db: Session = Depends(get_db)):
    """Customer credit summary"""
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    credit_summary = crud.get_customer_credit_summary(db, date_from=date_from_obj, date_to=date_to_obj)
    
    # Calculate overall totals
    total_customers = len(credit_summary)
    total_pending = sum(c['pending_count'] for c in credit_summary)
    total_due = sum(c['total_due'] for c in credit_summary)
    
    return templates.TemplateResponse('credit_summary.html', {
        "request": request,
        "credit_summary": credit_summary,
        "total_customers": total_customers,
        "total_pending": total_pending,
        "total_due": round(total_due, 2),
        "filters": {
            'date_from': date_from,
            'date_to': date_to
        }
    })

# Purchase Payment Routes
@app.get('/purchase-payments/pending', response_class=HTMLResponse)
def pending_purchase_payments(request: Request, db: Session = Depends(get_db)):
    """View pending purchase payments (amounts we owe suppliers)"""
    supplier_id = request.query_params.get('supplier_id')
    date_from = request.query_params.get('start_date')
    date_to = request.query_params.get('end_date')
    
    supplier_id_int = int(supplier_id) if supplier_id else None
    
    pending_purchases = crud.get_pending_purchase_payments(db, supplier_id=supplier_id_int)
    
    # Filter by date if provided
    if date_from or date_to:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
        
        filtered = []
        for purchase in pending_purchases:
            purchase_date = purchase.date.date() if hasattr(purchase.date, 'date') else purchase.date
            if date_from_obj and purchase_date < date_from_obj.date():
                continue
            if date_to_obj and purchase_date > date_to_obj.date():
                continue
            filtered.append(purchase)
        pending_purchases = filtered
    
    # Calculate summary stats
    total_due = sum(p.amount_due for p in pending_purchases)
    partial_count = sum(1 for p in pending_purchases if p.payment_status == 'partial')
    
    suppliers = db.query(models.Supplier).all()
    
    return templates.TemplateResponse('purchase_payments_pending.html', {
        "request": request,
        "pending_purchases": pending_purchases,
        "suppliers": suppliers,
        "total_due": round(total_due, 2),
        "partial_count": partial_count
    })

@app.get('/purchase-payments/record/{purchase_id}', response_class=HTMLResponse)
def record_purchase_payment_form(purchase_id: int, request: Request, db: Session = Depends(get_db)):
    """Show form to record a payment for a purchase"""
    purchase = db.query(models.Purchase).filter(models.Purchase.purchase_id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    payments = crud.get_payments_for_purchase(db, purchase_id)
    today = datetime.now().strftime('%Y-%m-%d')
    
    return templates.TemplateResponse('record_purchase_payment.html', {
        "request": request,
        "purchase": purchase,
        "payments": payments,
        "today": today
    })

@app.post('/purchase-payments/record/{purchase_id}')
async def record_purchase_payment_post(
    purchase_id: int,
    request: Request,
    amount: float = Form(...),
    payment_method: str = Form(...),
    payment_date: str = Form(...),
    reference_number: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Process a purchase payment"""
    try:
        payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d')
        
        payment = crud.add_purchase_payment(
            db,
            purchase_id=purchase_id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes
        )
        
        # Update payment date if different from default
        if payment_date_obj.date() != datetime.now().date():
            payment.payment_date = payment_date_obj
            db.commit()
        
        purchase = db.query(models.Purchase).filter(models.Purchase.purchase_id == purchase_id).first()
        payments = crud.get_payments_for_purchase(db, purchase_id)
        today = datetime.now().strftime('%Y-%m-%d')
        
        return templates.TemplateResponse('record_purchase_payment.html', {
            "request": request,
            "purchase": purchase,
            "payments": payments,
            "today": today,
            "message": f"Payment of Rs. {amount} recorded successfully! Remaining: Rs. {purchase.amount_due}"
        })
    
    except ValueError as e:
        purchase = db.query(models.Purchase).filter(models.Purchase.purchase_id == purchase_id).first()
        payments = crud.get_payments_for_purchase(db, purchase_id)
        today = datetime.now().strftime('%Y-%m-%d')
        
        return templates.TemplateResponse('record_purchase_payment.html', {
            "request": request,
            "purchase": purchase,
            "payments": payments,
            "today": today,
            "error": str(e)
        })

@app.get('/purchase-payments/history', response_class=HTMLResponse)
def purchase_payment_history(request: Request, db: Session = Depends(get_db)):
    """View purchase payment history"""
    supplier_id = request.query_params.get('supplier_id')
    payment_method = request.query_params.get('payment_method')
    date_from = request.query_params.get('start_date')
    date_to = request.query_params.get('end_date')
    
    supplier_id_int = int(supplier_id) if supplier_id else None
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    payments = crud.get_purchase_payment_history(db, supplier_id=supplier_id_int, date_from=date_from_obj, date_to=date_to_obj)
    
    # Filter by payment method if provided
    if payment_method:
        payments = [p for p in payments if p.payment_method == payment_method]
    
    # Calculate summary stats
    total_amount = sum(p.amount for p in payments)
    average_payment = total_amount / len(payments) if payments else 0
    
    suppliers = db.query(models.Supplier).all()
    
    return templates.TemplateResponse('purchase_payment_history.html', {
        "request": request,
        "payments": payments,
        "suppliers": suppliers,
        "total_amount": round(total_amount, 2),
        "average_payment": round(average_payment, 2),
        "filters": {
            'supplier_id': supplier_id,
            'payment_method': payment_method,
            'date_from': date_from,
            'date_to': date_to
        }
    })

@app.get('/purchase-payments/credit-summary', response_class=HTMLResponse)
def supplier_credit_summary(request: Request, db: Session = Depends(get_db)):
    """Supplier credit summary (amounts we owe)"""
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    credit_summary = crud.get_supplier_credit_summary(db, date_from=date_from_obj, date_to=date_to_obj)
    
    # Calculate overall totals
    total_suppliers = len(credit_summary)
    total_pending = sum(s['pending_count'] for s in credit_summary)
    total_due = sum(s['total_due'] for s in credit_summary)
    total_purchases = sum(s['total_purchases'] for s in credit_summary)
    average_due = total_due / total_suppliers if total_suppliers > 0 else 0
    
    # Calculate amounts paid
    credit_summary_with_paid = []
    for supplier in credit_summary:
        amount_paid = supplier['total_purchases'] - supplier['total_due']
        supplier['amount_paid'] = round(amount_paid, 2)
        credit_summary_with_paid.append(supplier)
    
    return templates.TemplateResponse('supplier_credit_summary.html', {
        "request": request,
        "credit_summary": credit_summary_with_paid,
        "suppliers_with_credit": total_suppliers,
        "total_credit": round(total_due, 2),
        "total_pending_invoices": total_pending,
        "average_credit": round(average_due, 2),
        "filters": {
            'date_from': date_from,
            'date_to': date_to
        }
    })

@app.get('/valuation', response_class=HTMLResponse)
def valuation_report(request: Request, db: Session = Depends(get_db)):
    # prepare FIFO lot-level details
    stock = crud.get_stock_summary(db)
    data = []
    for s in stock:
        # get lots and remaining per purchase
        lots = []
        total_sold = db.query(func.coalesce(func.sum(models.Sale.quantity_meters), 0)).filter(models.Sale.fabric_type==s['fabric_type'], models.Sale.fabric_code==s['fabric_code']).scalar() or 0
        purchases = db.query(models.Purchase).filter(models.Purchase.fabric_type==s['fabric_type'], models.Purchase.fabric_code==s['fabric_code']).order_by(models.Purchase.date.asc()).all()
        t_sold = float(total_sold)
        total_valuation = 0.0
        for p in purchases:
            lot_qty = float(p.quantity_meters)
            if t_sold >= lot_qty:
                t_sold -= lot_qty
                rem = 0.0
            else:
                rem = lot_qty - t_sold
                t_sold = 0.0
            val = round(rem * float(p.price_per_meter), 2)
            if rem > 0:
                lots.append({"date": p.date, "remaining": rem, "price_per_meter": p.price_per_meter, "value": val})
                total_valuation += val
        data.append({"fabric_type": s['fabric_type'], "fabric_code": s['fabric_code'], "composition": s['composition'], "lots": lots, "total_valuation": round(total_valuation,2)})
    return templates.TemplateResponse('valuation.html', {"request": request, "data": data})


@app.get('/export/purchases.csv')
def export_purchases(db: Session = Depends(get_db)):
    import csv, io
    purchases = db.query(models.Purchase).order_by(models.Purchase.date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['purchase_id','date','supplier','fabric_type','quantity_meters','price_per_meter','total_cost'])
    for p in purchases:
        writer.writerow([p.purchase_id, p.date, p.supplier.name if p.supplier else '', p.fabric_type, p.quantity_meters, p.price_per_meter, p.total_cost])
    return Response(content=output.getvalue(), media_type='text/csv')

@app.get('/database/export')
async def export_database(db: Session = Depends(get_db)):
    import shutil
    from datetime import datetime
    import os
    import sqlite3
    
    # Close the current database connection
    db.close()
    
    # Create a backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"fabric_backup_{timestamp}.db"
    
    try:
        # Verify database exists and is valid
        if not os.path.exists("fabric.db"):
            raise ValueError("Database file not found")
        
        # Validate database integrity before export
        try:
            conn = sqlite3.connect("fabric.db")
            cursor = conn.cursor()
            integrity_result = cursor.execute("PRAGMA integrity_check").fetchone()
            if integrity_result[0] != 'ok':
                raise ValueError(f"Database integrity check failed: {integrity_result[0]}")
            conn.close()
        except Exception as e:
            raise ValueError(f"Database integrity check failed: {str(e)}")
        
        # Create a copy of the database file
        shutil.copy2("fabric.db", backup_filename)
        
        # Verify the backup was created successfully
        if not os.path.exists(backup_filename):
            raise ValueError("Backup file creation failed")
        
        # Return the backup file
        # Create background tasks
        background_tasks = BackgroundTasks()
        background_tasks.add_task(os.remove, backup_filename)
        
        return FileResponse(
            backup_filename,
            media_type='application/octet-stream',
            filename=backup_filename,
            background=background_tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database export failed: {str(e)}")

@app.post('/database/import')
async def import_database(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import sqlite3
    import os
    from tempfile import NamedTemporaryFile
    from datetime import datetime
    import shutil
    
    # Close the current database connection
    db.close()
    
    try:
        # Save uploaded file to a temporary location
        with NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Validate that this is a valid SQLite database
        try:
            conn = sqlite3.connect(temp_path)
            
            # Check integrity
            cursor = conn.cursor()
            integrity_result = cursor.execute("PRAGMA integrity_check").fetchone()
            if integrity_result[0] != 'ok':
                raise ValueError(f"Database integrity check failed: {integrity_result[0]}")
            
            # Check if this is our database schema by verifying all required tables
            required_tables = {'companies', 'suppliers', 'customers', 'purchases', 'sales', 'payments', 'purchase_payments'}
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            # Check if minimum required tables exist
            core_tables = {'companies', 'suppliers', 'customers', 'purchases', 'sales'}
            if not core_tables.issubset(existing_tables):
                missing = core_tables - existing_tables
                raise ValueError(f"Invalid database schema: missing required tables: {', '.join(missing)}")
            
            # Warn if payment tables are missing but allow import
            missing_optional = required_tables - existing_tables
            if missing_optional:
                pass  # Silently allow - may be older version
                
        except sqlite3.Error as e:
            raise ValueError(f"Invalid SQLite database file: {str(e)}")
        
        # Create a backup of current database
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"fabric_backup_before_import_{backup_timestamp}.db"
        
        if os.path.exists("fabric.db"):
            shutil.copy2("fabric.db", backup_filename)
        
        # Replace the current database with the uploaded one
        shutil.copy2(temp_path, "fabric.db")
        
        # Verify the import was successful
        try:
            verify_conn = sqlite3.connect("fabric.db")
            verify_cursor = verify_conn.cursor()
            verify_result = verify_cursor.execute("PRAGMA integrity_check").fetchone()
            if verify_result[0] != 'ok':
                raise ValueError(f"Database verification failed after import: {verify_result[0]}")
            verify_conn.close()
        except Exception as e:
            # Restore from backup if verification fails
            if os.path.exists(backup_filename):
                shutil.copy2(backup_filename, "fabric.db")
            raise ValueError(f"Database verification after import failed: {str(e)}. Restored from backup.")
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return templates.TemplateResponse(
            "database_operations.html",
            {
                "request": request,
                "message": "✅ Database imported successfully! All data has been restored. Previous database backed up as: " + backup_filename,
                "backup_file": backup_filename
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database import failed: {str(e)}")


@app.get('/export/sales.csv')
def export_sales(db: Session = Depends(get_db)):
    import csv, io
    sales = db.query(models.Sale).order_by(models.Sale.date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['sale_id','date','customer','fabric_type','quantity_meters','price_per_meter','apply_tax','tax','total_price_with_tax'])
    for s in sales:
        writer.writerow([s.sale_id, s.date, s.customer.name if s.customer else '', s.fabric_type, s.quantity_meters, s.price_per_meter, s.apply_tax, s.tax, s.total_price_with_tax])
    return Response(content=output.getvalue(), media_type='text/csv')


@app.get('/export/stock.csv')
def export_stock(db: Session = Depends(get_db)):
    import csv, io
    stock = crud.get_stock_summary(db)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['fabric_type','total_purchased','total_sold','balance_in_meters','avg_cost_per_meter','stock_valuation'])
    for s in stock:
        writer.writerow([s['fabric_type'], s['total_purchased'], s['total_sold'], s['balance_in_meters'], s['avg_cost_per_meter'], s['stock_valuation']])
    return Response(content=output.getvalue(), media_type='text/csv')

# API endpoints
@app.post('/api/add_purchase')
def api_add_purchase(purchase: schemas.APIPurchase, db: Session = Depends(get_db)):
    p = crud.create_purchase(db, **purchase.dict())
    return {"purchase_id": p.purchase_id}

@app.post('/api/add_sale')
def api_add_sale(sale: schemas.APISale, db: Session = Depends(get_db)):
    try:
        # Convert tax_rate from percentage to decimal
        sale_data = sale.dict()
        if 'tax_rate' in sale_data:
            sale_data['tax_rate'] = sale_data['tax_rate'] / 100
        s = crud.create_sale(db, **sale_data)
        return {"sale_id": s.sale_id}
    except ValueError as e:
        return Response(status_code=400, content=str(e))

@app.get('/api/stock')
def api_stock(db: Session = Depends(get_db)):
    return crud.get_stock_summary(db)

@app.get('/api/purchases')
def api_purchases(db: Session = Depends(get_db)):
    return crud.get_purchases(db)

@app.get('/api/sales')
def api_sales(db: Session = Depends(get_db)):
    return crud.get_sales(db)

# Invoice PDF with optional company name parameter
# Invoice PDF
@app.get('/invoice/{sale_id}')
def invoice_pdf(sale_id: int, db: Session = Depends(get_db)):
    s = db.query(models.Sale).filter(models.Sale.sale_id==sale_id).first()
    if not s:
        raise HTTPException(status_code=404, detail='Sale not found')

    # Get company information
    company = None
    if s.company_id:
        company = crud.get_company_by_id(db, s.company_id)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Professional color scheme
    primary_blue = colors.HexColor('#1e3a8a')     # Deep navy blue
    accent_blue = colors.HexColor('#3b82f6')      # Medium blue
    light_blue = colors.HexColor('#eff6ff')       # Very light blue
    success_green = colors.HexColor('#059669')    # Success green
    text_dark = colors.HexColor('#1f2937')        # Dark gray text
    text_medium = colors.HexColor('#6b7280')      # Medium gray text
    text_light = colors.HexColor('#9ca3af')       # Light gray text
    
    y_pos = height - 30
    
    # Top header with gradient effect (simulated with rectangles)
    c.setFillColor(primary_blue)
    c.rect(0, height-100, width, 100, fill=1, stroke=0)
    
    # Add subtle shadow effect
    c.setFillColor(colors.HexColor('#1e40af'))
    c.rect(0, height-105, width, 5, fill=1, stroke=0)
    
    # Company Header
    if company:
        c.setFont('Helvetica-Bold', 26)
        c.setFillColor(colors.white)
        c.drawCentredString(width/2, y_pos-35, company.company_name.upper())
        
        # Company tagline or business type
        c.setFont('Helvetica-Oblique', 12)
        c.setFillColor(colors.HexColor('#bfdbfe'))
        c.drawCentredString(width/2, y_pos-55, "Professional Business Solutions")
        
        # Company details in elegant layout
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.white)
        
        details_y = y_pos - 75
        if company.address:
            c.drawString(60, details_y, f"📍 {company.address}")
        if company.phone:
            c.drawRightString(width-60, details_y, f"📞 {company.phone}")
        
        details_y -= 15
        if company.email:
            c.drawString(60, details_y, f"✉️ {company.email}")
        if company.website:
            c.drawRightString(width-60, details_y, f"🌐 {company.website}")
            
        if company.tax_number:
            details_y -= 15
            c.drawCentredString(width/2, details_y, f"Tax Registration: {company.tax_number}")
    else:
        c.setFont('Helvetica-Bold', 26)
        c.setFillColor(colors.white)
        c.drawCentredString(width/2, y_pos-35, "PROFESSIONAL INVOICE")
        
        c.setFont('Helvetica-Oblique', 12)
        c.setFillColor(colors.HexColor('#bfdbfe'))
        c.drawCentredString(width/2, y_pos-55, "Quality Business Solutions")
    
    # Reset position after header
    y_pos = height - 130
    
    # INVOICE banner with modern design
    c.setFillColor(accent_blue)
    c.rect(40, y_pos-35, width-80, 35, fill=1, stroke=0)
    
    # Add subtle border
    c.setStrokeColor(primary_blue)
    c.setLineWidth(2)
    c.rect(40, y_pos-35, width-80, 35, fill=0, stroke=1)
    
    c.setFont('Helvetica-Bold', 18)
    c.setFillColor(colors.white)
    c.drawCentredString(width/2, y_pos-22, "I N V O I C E")
    
    y_pos -= 60
    
    # Main content area with subtle background
    content_height = y_pos - 180
    c.setFillColor(colors.HexColor('#fafafa'))
    c.rect(40, 180, width-80, content_height, fill=1, stroke=0)
    
    # Invoice details card
    card_width = 220
    card_height = 85
    
    # Left card - Invoice details
    c.setFillColor(light_blue)
    c.setStrokeColor(accent_blue)
    c.setLineWidth(1)
    c.rect(60, y_pos-card_height, card_width, card_height, fill=1, stroke=1)
    
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(primary_blue)
    c.drawString(75, y_pos-20, "INVOICE DETAILS")
    
    c.setFont('Helvetica', 10)
    c.setFillColor(text_dark)
    c.drawString(75, y_pos-35, f"Invoice #: #{s.sale_id:06d}")
    c.drawString(75, y_pos-50, f"Date: {s.date.strftime('%B %d, %Y')}")
    c.drawString(75, y_pos-65, f"Time: {s.date.strftime('%I:%M %p')}")
    
    # Right card - Bill To
    c.setFillColor(light_blue)
    c.rect(width-280, y_pos-card_height, card_width, card_height, fill=1, stroke=1)
    
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(primary_blue)
    c.drawString(width-265, y_pos-20, "BILL TO")
    
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(text_dark)
    c.drawString(width-265, y_pos-38, s.customer.name)
    
    c.setFont('Helvetica', 9)
    c.setFillColor(text_medium)
    c.drawString(width-265, y_pos-52, f"Contact: {s.customer.contact or 'N/A'}")
    c.drawString(width-265, y_pos-65, f"Customer ID: {s.customer.customer_id}")
    
    y_pos -= 110
    
    # Items section with modern table design
    table_y = y_pos
    table_width = width - 120
    header_height = 35
    row_height = 45
    
    # Table header with gradient
    c.setFillColor(primary_blue)
    c.rect(60, table_y-header_height, table_width, header_height, fill=1, stroke=0)
    
    # Header shadow
    c.setFillColor(colors.HexColor('#1e40af'))
    c.rect(60, table_y-header_height-2, table_width, 2, fill=1, stroke=0)
    
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(colors.white)
    c.drawCentredString(160, table_y-22, "ITEM DESCRIPTION")
    c.drawCentredString(320, table_y-22, "QTY")
    c.drawCentredString(420, table_y-22, "RATE")
    c.drawCentredString(500, table_y-22, "AMOUNT")
    
    # Table row with alternating background
    row_y = table_y - header_height
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor('#e5e7eb'))
    c.setLineWidth(0.5)
    c.rect(60, row_y-row_height, table_width, row_height, fill=1, stroke=1)
    
    # Item details with better formatting
    c.setFont('Helvetica-Bold', 11)
    c.setFillColor(text_dark)
    item_y = row_y - 15
    c.drawString(70, item_y, s.fabric_type)
    
    c.setFont('Helvetica', 9)
    c.setFillColor(text_medium)
    if s.fabric_code:
        c.drawString(70, item_y-12, f"Code: {s.fabric_code}")
    if s.composition:
        c.drawString(70, item_y-24, f"Material: {s.composition}")
    
    # Quantity, Rate, Amount
    c.setFont('Helvetica', 10)
    c.setFillColor(text_dark)
    c.drawCentredString(320, row_y-20, f"{s.quantity_meters}")
    c.setFont('Helvetica', 8)
    c.setFillColor(text_medium)
    c.drawCentredString(320, row_y-32, "meters")
    
    c.setFont('Helvetica', 10)
    c.setFillColor(text_dark)
    c.drawCentredString(420, row_y-25, f"Rs. {s.price_per_meter:.2f}")
    
    subtotal = s.quantity_meters * s.price_per_meter
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(success_green)
    c.drawCentredString(500, row_y-25, f"Rs. {subtotal:.2f}")
    
    y_pos = row_y - row_height - 30
    
    # Summary section with cards
    summary_width = 280
    summary_x = width - summary_width - 60
    
    # Summary background
    c.setFillColor(colors.HexColor('#f9fafb'))
    c.setStrokeColor(colors.HexColor('#e5e7eb'))
    c.rect(summary_x, y_pos-90, summary_width, 90, fill=1, stroke=1)
    
    # Summary items
    c.setFont('Helvetica', 11)
    c.setFillColor(text_dark)
    
    summary_y = y_pos - 20
    c.drawString(summary_x + 20, summary_y, "Subtotal:")
    c.drawRightString(summary_x + summary_width - 20, summary_y, f"Rs. {subtotal:.2f}")
    
    summary_y -= 20
    if s.apply_tax:
        # Calculate the tax percentage from the tax amount
        tax_percentage = (s.tax / subtotal) * 100
        c.drawString(summary_x + 20, summary_y, f"Tax ({tax_percentage:.0f}%):")
        c.drawRightString(summary_x + summary_width - 20, summary_y, f"Rs. {s.tax:.2f}")
    else:
        c.setFillColor(text_medium)
        c.drawString(summary_x + 20, summary_y, "Tax:")
        c.drawRightString(summary_x + summary_width - 20, summary_y, "Not Applied")
    
    # Total section with highlight
    summary_y -= 30
    c.setFillColor(success_green)
    c.rect(summary_x + 10, summary_y-5, summary_width-20, 25, fill=1, stroke=0)
    
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(colors.white)
    c.drawString(summary_x + 20, summary_y+5, "TOTAL:")
    c.drawRightString(summary_x + summary_width - 20, summary_y+5, f"Rs. {s.total_price_with_tax:.2f}")
    
    y_pos -= 120
    
    # Footer section with modern styling
    footer_height = 70
    c.setFillColor(primary_blue)
    c.rect(40, y_pos-footer_height, width-80, footer_height, fill=1, stroke=0)
    
    # Footer content
    c.setFont('Helvetica-Bold', 14)
    c.setFillColor(colors.white)
    c.drawCentredString(width/2, y_pos-25, "Thank you for your business!")
    
    c.setFont('Helvetica', 10)
    c.setFillColor(colors.HexColor('#bfdbfe'))
    c.drawCentredString(width/2, y_pos-40, "For support & inquiries: WhatsApp 03362793950")
    
    c.setFont('Helvetica-Oblique', 8)
    c.setFillColor(colors.HexColor('#93c5fd'))
    c.drawCentredString(width/2, y_pos-55, f"Generated on {s.date.strftime('%B %d, %Y at %I:%M %p')} • Secure Digital Invoice")
    
    # Bottom branding strip
    c.setFillColor(colors.HexColor('#f8fafc'))
    c.rect(0, 0, width, 35, fill=1, stroke=0)
    
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(primary_blue)
    c.drawCentredString(width/2, 20, "Powered by TzkSolution")
    
    c.setFont('Helvetica', 8)
    c.setFillColor(text_medium)
    c.drawCentredString(width/2, 10, "Professional Invoice Management System • WhatsApp: 03362793950")

    c.showPage()
    c.save()
    buffer.seek(0)
    
    # Set proper filename for download
    filename = f"Invoice_{s.sale_id:06d}_{s.customer.name.replace(' ', '_')}.pdf"
    
    return StreamingResponse(
        buffer, 
        media_type='application/pdf',
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


# ===================== BANK STATEMENT ROUTES =====================

@app.get('/bank/add-entry', response_class=HTMLResponse)
def bank_add_entry_form(request: Request):
    """Form to add manual bank entry"""
    return templates.TemplateResponse('bank_add_entry.html', {"request": request})

@app.get('/bank/statement', response_class=HTMLResponse)
def bank_statement_view(request: Request, db: Session = Depends(get_db)):
    """View complete bank statement with filters"""
    transaction_type = request.query_params.get('type')
    status = request.query_params.get('status')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    bank_account = request.query_params.get('bank_account')
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    statements = crud.get_bank_statements(
        db,
        transaction_type=transaction_type,
        status=status,
        date_from=date_from_obj,
        date_to=date_to_obj,
        bank_account=bank_account
    )
    
    summary = crud.get_bank_summary(db, date_from=date_from_obj, date_to=date_to_obj, bank_account=bank_account)
    
    # Get unique bank accounts for filter
    all_statements = db.query(models.BankStatement).all()
    bank_accounts = list(set([s.bank_account for s in all_statements if s.bank_account]))
    
    return templates.TemplateResponse('bank_statement.html', {
        "request": request,
        "statements": summary['statements'],
        "summary": summary,
        "bank_accounts": bank_accounts,
        "filters": {
            'type': transaction_type,
            'status': status,
            'date_from': date_from,
            'date_to': date_to,
            'bank_account': bank_account
        }
    })

@app.get('/bank/dashboard', response_class=HTMLResponse)
def bank_dashboard(request: Request, db: Session = Depends(get_db)):
    """Bank dashboard with overview and reconciliation"""
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    summary = crud.get_bank_summary(db, date_from=date_from_obj, date_to=date_to_obj)
    reconciliation = crud.get_bank_reconciliation_status(db, date_from=date_from_obj, date_to=date_to_obj)
    
    return templates.TemplateResponse('bank_dashboard.html', {
        "request": request,
        "summary": summary,
        "reconciliation": reconciliation,
        "filters": {
            'date_from': date_from,
            'date_to': date_to
        }
    })

@app.get('/bank/reconciliation', response_class=HTMLResponse)
def bank_reconciliation(request: Request, db: Session = Depends(get_db)):
    """Bank reconciliation view with pending and cleared transactions"""
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    reconciliation = crud.get_bank_reconciliation_status(db, date_from=date_from_obj, date_to=date_to_obj)
    
    return templates.TemplateResponse('bank_reconciliation.html', {
        "request": request,
        "reconciliation": reconciliation,
        "filters": {
            'date_from': date_from,
            'date_to': date_to
        }
    })

@app.post('/bank/update-status/{statement_id}')
def update_bank_statement_status(
    statement_id: int,
    status: str = Form(...),
    reconciliation_notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update bank statement status (pending, cleared, failed)"""
    try:
        statement = crud.update_bank_statement(
            db,
            statement_id=statement_id,
            status=status,
            reconciliation_notes=reconciliation_notes
        )
        return {"ok": True, "message": f"Bank statement status updated to '{status}'"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/bank/manual-entry')
def add_manual_bank_entry(
    request: Request,
    transaction_type: str = Form(...),
    amount: float = Form(...),
    description: str = Form(...),
    bank_account: str = Form(None),
    reference_number: str = Form(None),
    payment_method: str = Form(None),
    status: str = Form('cleared'),
    db: Session = Depends(get_db)
):
    """Add manual bank statement entry"""
    try:
        statement = crud.add_bank_statement(
            db,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            bank_account=bank_account,
            reference_number=reference_number,
            payment_method=payment_method,
            status=status
        )
        # Redirect to bank statement with success message
        return RedirectResponse(url="/bank/statement?added=true", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse('bank_add_entry.html', {
            "request": request,
            "error": str(e)
        })

@app.get('/bank/export.csv')
def export_bank_statement(
    type: str = None,
    status: str = None,
    date_from: str = None,
    date_to: str = None,
    bank_account: str = None,
    db: Session = Depends(get_db)
):
    """Export bank statement as CSV"""
    import csv, io
    
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    statements = crud.get_bank_statements(
        db,
        transaction_type=type,
        status=status,
        date_from=date_from_obj,
        date_to=date_to_obj,
        bank_account=bank_account
    )
    
    summary = crud.get_bank_summary(db, date_from=date_from_obj, date_to=date_to_obj, bank_account=bank_account)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Description', 'Amount', 'Account', 'Reference', 'Status', 'Payment Method'])
    
    for s in statements:
        writer.writerow([
            s.transaction_date.strftime('%Y-%m-%d %H:%M'),
            s.transaction_type.upper(),
            s.description,
            s.amount,
            s.bank_account or '',
            s.reference_number or '',
            s.status,
            s.payment_method or ''
        ])
    
    # Add summary
    writer.writerow([])
    writer.writerow(['SUMMARY', '', '', '', '', '', '', ''])
    writer.writerow(['Opening Balance', '', '', summary['opening_balance'], '', '', '', ''])
    writer.writerow(['Total Credits', '', '', summary['total_credit'], '', '', '', ''])
    writer.writerow(['Total Debits', '', '', summary['total_debit'], '', '', '', ''])
    writer.writerow(['Closing Balance', '', '', summary['closing_balance'], '', '', '', ''])
    
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename=bank_statement_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
    )

# Bank API endpoints
@app.get('/api/bank/summary')
def api_bank_summary(date_from: str = None, date_to: str = None, db: Session = Depends(get_db)):
    """Get bank summary via API"""
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    return crud.get_bank_summary(db, date_from=date_from_obj, date_to=date_to_obj)

@app.get('/api/bank/reconciliation')
def api_bank_reconciliation(date_from: str = None, date_to: str = None, db: Session = Depends(get_db)):
    """Get reconciliation status via API"""
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    return crud.get_bank_reconciliation_status(db, date_from=date_from_obj, date_to=date_to_obj)

@app.get('/api/bank/statements')
def api_bank_statements(
    type: str = None,
    status: str = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db)
):
    """Get bank statements via API"""
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d') if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') if date_to else None
    
    statements = crud.get_bank_statements(
        db,
        transaction_type=type,
        status=status,
        date_from=date_from_obj,
        date_to=date_to_obj
    )
    
    return [{
        'statement_id': s.statement_id,
        'date': s.transaction_date.isoformat(),
        'type': s.transaction_type,
        'amount': s.amount,
        'description': s.description,
        'status': s.status
    } for s in statements]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
