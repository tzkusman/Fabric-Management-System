"""
Migration script to add payment tracking fields to sales table
and create payments table
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'fabric.db')
DB_PATH = os.path.abspath(DB_PATH)
print('DB path:', DB_PATH)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def try_alter(sql, name):
    """Idempotent: check whether column/table exists first"""
    if '.' in name:
        table, col = name.split('.', 1)
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        if col in cols:
            print(f'✓ Skipping {name}, already exists')
            return
    else:
        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
        if cur.fetchone():
            print(f'✓ Skipping table {name}, already exists')
            return
    
    try:
        cur.execute(sql)
        print(f'✓ Added {name}')
    except Exception as e:
        print(f'✗ Could not add {name}:', e)

# Add payment tracking columns to sales table
print('\n=== Adding Payment Tracking Columns to Sales ===')
try_alter("ALTER TABLE sales ADD COLUMN payment_method TEXT DEFAULT 'cash';", 'sales.payment_method')
try_alter("ALTER TABLE sales ADD COLUMN payment_status TEXT DEFAULT 'paid';", 'sales.payment_status')
try_alter("ALTER TABLE sales ADD COLUMN amount_paid REAL DEFAULT 0.0;", 'sales.amount_paid')
try_alter("ALTER TABLE sales ADD COLUMN amount_due REAL DEFAULT 0.0;", 'sales.amount_due')
try_alter("ALTER TABLE sales ADD COLUMN payment_notes TEXT;", 'sales.payment_notes')

# Create payments table
print('\n=== Creating Payments Table ===')
try_alter("""
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    reference_number TEXT,
    notes TEXT,
    recorded_by TEXT,
    FOREIGN KEY (sale_id) REFERENCES sales (sale_id)
);
""", 'payments')

# Update existing sales to have proper payment values
print('\n=== Updating Existing Sales ===')
try:
    # Set amount_paid = total_price_with_tax for existing sales (assuming they were paid)
    cur.execute("""
        UPDATE sales 
        SET amount_paid = total_price_with_tax,
            amount_due = 0.0,
            payment_method = 'cash',
            payment_status = 'paid'
        WHERE amount_paid = 0.0 OR amount_paid IS NULL
    """)
    print(f'✓ Updated {cur.rowcount} existing sales records')
except Exception as e:
    print(f'✗ Could not update existing sales:', e)

conn.commit()
conn.close()
print('\n=== Migration Completed Successfully! ===')
