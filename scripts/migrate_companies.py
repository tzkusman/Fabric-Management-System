import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'fabric.db')
DB_PATH = os.path.abspath(DB_PATH)
print('DB path:', DB_PATH)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def try_alter(sql, name):
    # idempotent: check whether column exists first
    table, col = name.split('.', 1)
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    if col in cols:
        print(f'skipping {name}, already exists')
        return
    try:
        cur.execute(sql)
        print(f'OK added {name}')
    except Exception as e:
        print(f'Could not add {name}:', e)

def create_table_if_not_exists(table_sql, table_name):
    try:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cur.fetchone():
            print(f'Table {table_name} already exists')
        else:
            cur.execute(table_sql)
            print(f'Created table {table_name}')
    except Exception as e:
        print(f'Could not create table {table_name}:', e)

# Create companies table
companies_table_sql = """
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    address TEXT,
    phone TEXT,
    email TEXT,
    tax_number TEXT,
    license_number TEXT,
    website TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
create_table_if_not_exists(companies_table_sql, 'companies')

# Add company_id to sales table
try_alter("ALTER TABLE sales ADD COLUMN company_id INTEGER REFERENCES companies(company_id);", 'sales.company_id')

conn.commit()
conn.close()
print('Company migration finished')