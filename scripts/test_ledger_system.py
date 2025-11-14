"""
Test script for Ledger System functionality
Tests all ledger functions with sample data
"""

from database import SessionLocal
import models, crud
from datetime import datetime, timedelta

def test_ledger_system():
    db = SessionLocal()
    print("=" * 60)
    print("TESTING LEDGER SYSTEM")
    print("=" * 60)
    
    try:
        # Test 1: Get all purchases ledger
        print("\n1. Testing Purchase Ledger (All Records)")
        print("-" * 60)
        purchase_ledger = crud.get_purchase_ledger(db)
        print(f"   Total Purchases: {purchase_ledger['count']}")
        print(f"   Total Quantity: {purchase_ledger['total_quantity']} meters")
        print(f"   Total Amount: Rs. {purchase_ledger['total_amount']}")
        
        # Test 2: Get sales ledger
        print("\n2. Testing Sales Ledger (All Records)")
        print("-" * 60)
        sales_ledger = crud.get_sale_ledger(db)
        print(f"   Total Sales: {sales_ledger['count']}")
        print(f"   Total Quantity: {sales_ledger['total_quantity']} meters")
        print(f"   Subtotal: Rs. {sales_ledger['subtotal']}")
        print(f"   Total Tax: Rs. {sales_ledger['total_tax']}")
        print(f"   Grand Total: Rs. {sales_ledger['total_amount']}")
        
        # Test 3: Date range filtering
        print("\n3. Testing Date Range Filter (Last 30 days)")
        print("-" * 60)
        date_from = datetime.now() - timedelta(days=30)
        purchase_ledger_30 = crud.get_purchase_ledger(db, date_from=date_from)
        sales_ledger_30 = crud.get_sale_ledger(db, date_from=date_from)
        print(f"   Purchases (Last 30 days): {purchase_ledger_30['count']}")
        print(f"   Sales (Last 30 days): {sales_ledger_30['count']}")
        
        # Test 4: Customer summary
        print("\n4. Testing Customer Ledger Summary")
        print("-" * 60)
        customer_summary = crud.get_customer_ledger_summary(db)
        print(f"   Active Customers: {len(customer_summary)}")
        if customer_summary:
            print("\n   Top 3 Customers by Revenue:")
            sorted_customers = sorted(customer_summary, key=lambda x: x['total_amount'], reverse=True)[:3]
            for i, customer in enumerate(sorted_customers, 1):
                print(f"      {i}. {customer['customer_name']}: Rs. {customer['total_amount']} ({customer['transaction_count']} transactions)")
        
        # Test 5: Supplier summary
        print("\n5. Testing Supplier Ledger Summary")
        print("-" * 60)
        supplier_summary = crud.get_supplier_ledger_summary(db)
        print(f"   Active Suppliers: {len(supplier_summary)}")
        if supplier_summary:
            print("\n   Top 3 Suppliers by Spending:")
            sorted_suppliers = sorted(supplier_summary, key=lambda x: x['total_amount'], reverse=True)[:3]
            for i, supplier in enumerate(sorted_suppliers, 1):
                print(f"      {i}. {supplier['supplier_name']}: Rs. {supplier['total_amount']} ({supplier['transaction_count']} transactions)")
        
        # Test 6: Specific customer filter
        if customer_summary:
            test_customer_id = customer_summary[0]['customer_id']
            print(f"\n6. Testing Customer-Specific Filter (Customer ID: {test_customer_id})")
            print("-" * 60)
            customer_sales = crud.get_sale_ledger(db, customer_id=test_customer_id)
            print(f"   Sales for this customer: {customer_sales['count']}")
            print(f"   Total Amount: Rs. {customer_sales['total_amount']}")
        
        # Test 7: Tax filter
        print("\n7. Testing Tax Filter (Sales with Tax)")
        print("-" * 60)
        taxed_sales = crud.get_sale_ledger(db, apply_tax_filter=True)
        non_taxed_sales = crud.get_sale_ledger(db, apply_tax_filter=False)
        print(f"   Sales WITH tax: {taxed_sales['count']}")
        print(f"   Sales WITHOUT tax: {non_taxed_sales['count']}")
        
        # Test 8: Search functionality
        print("\n8. Testing Search Filter")
        print("-" * 60)
        search_results = crud.get_purchase_ledger(db, search_query="cotton")
        print(f"   Purchases matching 'cotton': {search_results['count']}")
        
        print("\n" + "=" * 60)
        print("ALL LEDGER TESTS COMPLETED SUCCESSFULLY! ✓")
        print("=" * 60)
        
        # Display sample records if available
        if purchase_ledger['purchases']:
            print("\nSample Purchase Record:")
            p = purchase_ledger['purchases'][0]
            print(f"   ID: {p.purchase_id}")
            print(f"   Date: {p.date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Supplier: {p.supplier.name}")
            print(f"   Fabric: {p.fabric_type}")
            print(f"   Quantity: {p.quantity_meters}m")
            print(f"   Total: Rs. {p.total_cost}")
        
        if sales_ledger['sales']:
            print("\nSample Sale Record:")
            s = sales_ledger['sales'][0]
            print(f"   ID: {s.sale_id}")
            print(f"   Date: {s.date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Customer: {s.customer.name}")
            print(f"   Fabric: {s.fabric_type}")
            print(f"   Quantity: {s.quantity_meters}m")
            print(f"   Tax Applied: {'Yes' if s.apply_tax else 'No'}")
            print(f"   Total: Rs. {s.total_price_with_tax}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_ledger_system()
