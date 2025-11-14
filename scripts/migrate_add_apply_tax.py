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

# Add apply_tax column with default value True (1) for existing records
try_alter("ALTER TABLE sales ADD COLUMN apply_tax BOOLEAN NOT NULL DEFAULT 1;", 'sales.apply_tax')

conn.commit()
conn.close()
print('Migration finished')