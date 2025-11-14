import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import engine
from sqlalchemy import text

def add_tax_rate_column():
    with engine.connect() as conn:
        # Add the column if it doesn't exist
        try:
            conn.execute(text("ALTER TABLE sales ADD COLUMN tax_rate FLOAT"))
            conn.commit()
        except Exception as e:
            print(f"Column may already exist: {e}")
            
        # Update existing records
        conn.execute(text("""
            UPDATE sales 
            SET tax_rate = CASE 
                WHEN apply_tax = 1 AND (quantity_meters * price_per_meter) > 0 
                THEN ROUND(CAST(tax AS FLOAT) / (quantity_meters * price_per_meter), 4)
                ELSE 0 
            END
            WHERE tax_rate IS NULL
        """))
        conn.commit()

if __name__ == '__main__':
    add_tax_rate_column()