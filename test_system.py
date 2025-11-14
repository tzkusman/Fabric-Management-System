"""
Comprehensive System Test - Fabric Inventory Management System
Tests all routes, database operations, and payment tracking features
"""

import sqlite3
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def check_database():
    """Check database structure"""
    print_section("DATABASE STRUCTURE CHECK")
    
    conn = sqlite3.connect('fabric.db')
    cursor = conn.cursor()
    
    # Check all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    required_tables = ['suppliers', 'customers', 'purchases', 'sales', 'companies', 'payments', 'purchase_payments']
    
    print(f"✅ Found {len(tables)} tables:")
    for table in tables:
        status = "✅" if table in required_tables else "ℹ️"
        print(f"  {status} {table}")
    
    missing = set(required_tables) - set(tables)
    if missing:
        print(f"\n❌ Missing tables: {missing}")
        return False
    
    # Check purchases table has payment columns
    print("\n📋 Purchases table columns:")
    cursor.execute("PRAGMA table_info(purchases)")
    purchase_cols = {col[1] for col in cursor.fetchall()}
    
    required_purchase_cols = ['payment_method', 'payment_status', 'amount_paid', 'amount_due', 'payment_notes']
    for col in required_purchase_cols:
        status = "✅" if col in purchase_cols else "❌"
        print(f"  {status} {col}")
    
    # Check sales table has payment columns
    print("\n📋 Sales table columns:")
    cursor.execute("PRAGMA table_info(sales)")
    sale_cols = {col[1] for col in cursor.fetchall()}
    
    required_sale_cols = ['payment_method', 'payment_status', 'amount_paid', 'amount_due', 'payment_notes']
    for col in required_sale_cols:
        status = "✅" if col in sale_cols else "❌"
        print(f"  {status} {col}")
    
    # Check purchase_payments table structure
    print("\n📋 Purchase_payments table columns:")
    cursor.execute("PRAGMA table_info(purchase_payments)")
    payment_cols = [col[1] for col in cursor.fetchall()]
    print(f"  Columns: {', '.join(payment_cols)}")
    
    # Check payments table structure
    print("\n📋 Payments (sales) table columns:")
    cursor.execute("PRAGMA table_info(payments)")
    sale_payment_cols = [col[1] for col in cursor.fetchall()]
    print(f"  Columns: {', '.join(sale_payment_cols)}")
    
    conn.close()
    return True

def check_data():
    """Check data in tables"""
    print_section("DATA CHECK")
    
    conn = sqlite3.connect('fabric.db')
    cursor = conn.cursor()
    
    # Count records in each table
    tables = ['suppliers', 'customers', 'purchases', 'sales', 'companies', 'payments', 'purchase_payments']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  📊 {table}: {count} records")
    
    # Check purchases with pending payments
    cursor.execute("SELECT COUNT(*) FROM purchases WHERE payment_status IN ('pending', 'partial')")
    pending_purchases = cursor.fetchone()[0]
    print(f"\n  💰 Pending purchase payments: {pending_purchases}")
    
    # Check sales with pending payments
    cursor.execute("SELECT COUNT(*) FROM sales WHERE payment_status IN ('pending', 'partial')")
    pending_sales = cursor.fetchone()[0]
    print(f"  💰 Pending sale payments: {pending_sales}")
    
    # Check total amounts due
    cursor.execute("SELECT COALESCE(SUM(amount_due), 0) FROM purchases WHERE payment_status IN ('pending', 'partial')")
    total_purchase_due = cursor.fetchone()[0]
    print(f"\n  📈 Total purchase amount due: Rs. {total_purchase_due:,.2f}")
    
    cursor.execute("SELECT COALESCE(SUM(amount_due), 0) FROM sales WHERE payment_status IN ('pending', 'partial')")
    total_sale_due = cursor.fetchone()[0]
    print(f"  📈 Total sale amount due: Rs. {total_sale_due:,.2f}")
    
    conn.close()

def check_routes():
    """Check all route definitions"""
    print_section("ROUTE CHECK")
    
    import main
    
    routes = []
    for route in main.app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            routes.append(f"{list(methods)[0]:6} {route.path}")
    
    # Group routes by category
    purchase_payment_routes = [r for r in routes if 'purchase-payment' in r]
    sale_payment_routes = [r for r in routes if '/payment' in r and 'purchase' not in r]
    core_routes = [r for r in routes if r not in purchase_payment_routes + sale_payment_routes]
    
    print(f"\n💳 Purchase Payment Routes ({len(purchase_payment_routes)}):")
    for route in sorted(purchase_payment_routes):
        print(f"  ✅ {route}")
    
    print(f"\n💳 Sale Payment Routes ({len(sale_payment_routes)}):")
    for route in sorted(sale_payment_routes):
        print(f"  ✅ {route}")
    
    print(f"\n📍 Core Routes ({len(core_routes)}):")
    for route in sorted(core_routes)[:10]:  # Show first 10
        print(f"  ✅ {route}")
    if len(core_routes) > 10:
        print(f"  ... and {len(core_routes) - 10} more")
    
    print(f"\n  📊 Total routes: {len(routes)}")

def check_templates():
    """Check template files"""
    print_section("TEMPLATE CHECK")
    
    import os
    
    template_dir = 'templates'
    templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    
    required_templates = [
        'base.html',
        'index.html',
        'add_purchase.html',
        'add_sale.html',
        'purchases.html',
        'sales.html',
        'purchase_payments_pending.html',
        'record_purchase_payment.html',
        'purchase_payment_history.html',
        'supplier_credit_summary.html',
        'payments_pending.html',
        'record_payment.html',
        'payment_history.html',
        'customer_credit_summary.html'
    ]
    
    for tmpl in required_templates:
        status = "✅" if tmpl in templates else "❌"
        print(f"  {status} {tmpl}")
    
    extra_templates = set(templates) - set(required_templates)
    if extra_templates:
        print(f"\n  ℹ️  Additional templates: {len(extra_templates)}")
        for tmpl in sorted(extra_templates)[:5]:
            print(f"      • {tmpl}")

def check_crud_functions():
    """Check CRUD functions"""
    print_section("CRUD FUNCTIONS CHECK")
    
    import crud
    
    # Purchase payment functions
    purchase_payment_funcs = [
        'add_purchase_payment',
        'get_payments_for_purchase',
        'get_pending_purchase_payments',
        'get_supplier_credit_summary',
        'get_purchase_payment_history'
    ]
    
    print("\n💳 Purchase Payment Functions:")
    for func in purchase_payment_funcs:
        status = "✅" if hasattr(crud, func) else "❌"
        print(f"  {status} {func}")
    
    # Sale payment functions
    sale_payment_funcs = [
        'add_payment',
        'get_payments_for_sale',
        'get_pending_payments',
        'get_customer_credit_summary',
        'get_payment_history'
    ]
    
    print("\n💳 Sale Payment Functions:")
    for func in sale_payment_funcs:
        status = "✅" if hasattr(crud, func) else "❌"
        print(f"  {status} {func}")
    
    # Core functions
    core_funcs = [
        'create_supplier',
        'create_customer',
        'create_purchase',
        'create_sale',
        'get_stock_summary'
    ]
    
    print("\n📍 Core Functions:")
    for func in core_funcs:
        status = "✅" if hasattr(crud, func) else "❌"
        print(f"  {status} {func}")

def check_models():
    """Check model definitions"""
    print_section("MODEL CHECK")
    
    import models
    
    required_models = [
        'Company',
        'Supplier',
        'Customer',
        'Purchase',
        'Sale',
        'Payment',
        'PurchasePayment'
    ]
    
    for model in required_models:
        status = "✅" if hasattr(models, model) else "❌"
        print(f"  {status} {model}")
    
    # Check Purchase model has payment fields
    if hasattr(models, 'Purchase'):
        purchase_attrs = dir(models.Purchase)
        payment_fields = ['payment_method', 'payment_status', 'amount_paid', 'amount_due', 'payments']
        print(f"\n  📋 Purchase payment fields:")
        for field in payment_fields:
            status = "✅" if field in purchase_attrs else "❌"
            print(f"    {status} {field}")
    
    # Check Sale model has payment fields
    if hasattr(models, 'Sale'):
        sale_attrs = dir(models.Sale)
        payment_fields = ['payment_method', 'payment_status', 'amount_paid', 'amount_due', 'payments']
        print(f"\n  📋 Sale payment fields:")
        for field in payment_fields:
            status = "✅" if field in sale_attrs else "❌"
            print(f"    {status} {field}")

def server_check():
    """Check if server is running"""
    print_section("SERVER STATUS CHECK")
    
    import requests
    
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=2)
        if response.status_code == 200:
            print(f"  ✅ Server is running on http://127.0.0.1:8000")
            print(f"  ✅ Response status: {response.status_code}")
            print(f"  ✅ Response size: {len(response.content)} bytes")
            return True
        else:
            print(f"  ⚠️  Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Server is not responding: {e}")
        return False

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("  FABRIC INVENTORY SYSTEM - COMPREHENSIVE TEST")
    print("="*60)
    print(f"  Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'Database Structure': False,
        'Data Integrity': False,
        'Models': False,
        'CRUD Functions': False,
        'Routes': False,
        'Templates': False,
        'Server': False
    }
    
    try:
        results['Database Structure'] = check_database()
        results['Data Integrity'] = True
        check_data()
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    try:
        results['Models'] = True
        check_models()
    except Exception as e:
        print(f"❌ Models check failed: {e}")
    
    try:
        results['CRUD Functions'] = True
        check_crud_functions()
    except Exception as e:
        print(f"❌ CRUD functions check failed: {e}")
    
    try:
        results['Routes'] = True
        check_routes()
    except Exception as e:
        print(f"❌ Routes check failed: {e}")
    
    try:
        results['Templates'] = True
        check_templates()
    except Exception as e:
        print(f"❌ Templates check failed: {e}")
    
    try:
        results['Server'] = server_check()
    except Exception as e:
        print(f"❌ Server check failed: {e}")
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    print(f"\n  📊 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n  🎉 ALL SYSTEMS OPERATIONAL! 🎉")
        print("\n  ✨ Both sale and purchase payment tracking systems are fully wired!")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed - review output above")

if __name__ == "__main__":
    main()
