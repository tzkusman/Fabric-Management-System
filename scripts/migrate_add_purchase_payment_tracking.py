"""
Migration script to add payment tracking to purchases table and create purchase_payments table
Run this script once to update your database schema
"""
import sqlite3
from datetime import datetime

DB_PATH = "fabric.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Starting migration for purchase payment tracking...")
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(purchases)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add payment tracking columns to purchases table if they don't exist
    if 'payment_method' not in columns:
        print("Adding payment_method column...")
        cursor.execute("ALTER TABLE purchases ADD COLUMN payment_method VARCHAR DEFAULT 'cash'")
    
    if 'payment_status' not in columns:
        print("Adding payment_status column...")
        cursor.execute("ALTER TABLE purchases ADD COLUMN payment_status VARCHAR DEFAULT 'paid'")
    
    if 'amount_paid' not in columns:
        print("Adding amount_paid column...")
        cursor.execute("ALTER TABLE purchases ADD COLUMN amount_paid REAL DEFAULT 0")
    
    if 'amount_due' not in columns:
        print("Adding amount_due column...")
        cursor.execute("ALTER TABLE purchases ADD COLUMN amount_due REAL DEFAULT 0")
    
    if 'payment_notes' not in columns:
        print("Adding payment_notes column...")
        cursor.execute("ALTER TABLE purchases ADD COLUMN payment_notes TEXT")
    
    # Update existing purchases to have payment_method='cash' and payment_status='paid'
    print("Updating existing purchases...")
    cursor.execute("""
        UPDATE purchases 
        SET payment_method = 'cash',
            payment_status = 'paid',
            amount_paid = total_cost,
            amount_due = 0
        WHERE payment_method IS NULL OR payment_status IS NULL
    """)
    
    updated_count = cursor.rowcount
    print(f"Updated {updated_count} existing purchases with default payment values")
    
    # Create purchase_payments table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,
            payment_date DATETIME NOT NULL,
            amount REAL NOT NULL,
            payment_method VARCHAR NOT NULL,
            reference_number VARCHAR,
            notes TEXT,
            recorded_by VARCHAR,
            FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE
        )
    """)
    print("Created purchase_payments table")
    
    conn.commit()
    conn.close()
    
    print("✅ Migration completed successfully!")
    print(f"   - Added 5 payment tracking columns to purchases table")
    print(f"   - Updated {updated_count} existing purchases")
    print(f"   - Created purchase_payments table for payment history")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
