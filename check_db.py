import sqlite3

conn = sqlite3.connect('fabric.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("=== DATABASE TABLES ===")
for table in tables:
    table_name = table[0]
    print(f"\n{table_name}:")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

# Check for payment-related tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%payment%'")
payment_tables = cursor.fetchall()
print("\n=== PAYMENT TABLES ===")
for table in payment_tables:
    print(f"  {table[0]}")

# Check purchases table columns
cursor.execute("PRAGMA table_info(purchases)")
purchase_columns = cursor.fetchall()
print("\n=== PURCHASES TABLE COLUMNS ===")
for col in purchase_columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
print("\n✅ Database check complete!")
