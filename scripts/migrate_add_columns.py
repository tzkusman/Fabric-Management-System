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

try_alter("ALTER TABLE purchases ADD COLUMN fabric_code TEXT;", 'purchases.fabric_code')
try_alter("ALTER TABLE purchases ADD COLUMN composition TEXT;", 'purchases.composition')
try_alter("ALTER TABLE sales ADD COLUMN fabric_code TEXT;", 'sales.fabric_code')
try_alter("ALTER TABLE sales ADD COLUMN composition TEXT;", 'sales.composition')

conn.commit()
conn.close()
print('Migration finished')
