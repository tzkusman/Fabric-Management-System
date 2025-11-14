from fastapi.testclient import TestClient
import sys
sys.path.insert(0, 'G:/p1/fabric inventory')
from main import app

client = TestClient(app)

def test_create_supplier_and_purchase_and_sale():
    # create supplier
    r = client.post('/add_supplier', data={'name':'t1','contact':'c1'})
    assert r.status_code in (200,307)
    # create customer
    r = client.post('/add_customer', data={'name':'cust','contact':'c'})
    assert r.status_code in (200,307)
    # create purchase via API
    buy = {'supplier_id':1,'fabric_type':'TestFabric','quantity_meters':10,'price_per_meter':5}
    r = client.post('/api/add_purchase', json=buy)
    assert r.status_code==200
    # create sale within stock
    sell = {'customer_id':1,'fabric_type':'TestFabric','quantity_meters':2,'price_per_meter':8}
    r = client.post('/api/add_sale', json=sell)
    assert r.status_code==200

