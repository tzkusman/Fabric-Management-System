from database import SessionLocal, engine
import models, crud
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
# create test data
s = crud.create_supplier(db, 'AutoSup','auto')
c = crud.create_customer(db, 'AutoCust','auto')
# create a purchase of 10 meters
p = crud.create_purchase(db, supplier_id=s.supplier_id, fabric_type='TestFab', quantity_meters=10.0, price_per_meter=20.0, fabric_code='T001')
print('Purchase id', p.purchase_id)
# create sale of 4 meters
try:
    sale = crud.create_sale(db, customer_id=c.customer_id, fabric_type='TestFab', quantity_meters=4.0, price_per_meter=30.0, fabric_code='T001')
    print('Sale id', sale.sale_id)
except Exception as e:
    print('Sale failed:', e)
# print stock summary
print('Stock summary:', crud.get_stock_summary(db))
