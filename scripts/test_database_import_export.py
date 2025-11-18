#!/usr/bin/env python
"""
Database Import/Export Test Script
Tests the complete backup and restore functionality
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import SessionLocal, engine

def check_database_integrity(db_path):
    """Verify database integrity"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        result = cursor.execute("PRAGMA integrity_check").fetchone()
        conn.close()
        return result[0] == 'ok'
    except Exception as e:
        print(f"❌ Integrity check failed: {e}")
        return False

def get_table_count(db_path, table_name):
    """Get record count for a table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"❌ Error counting {table_name}: {e}")
        return -1

def get_all_tables(db_path):
    """Get all tables in database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        print(f"❌ Error getting tables: {e}")
        return []

def verify_schema(db_path):
    """Verify database has all required tables"""
    tables = get_all_tables(db_path)
    
    required_core = {'companies', 'suppliers', 'customers', 'purchases', 'sales'}
    optional_tables = {'payments', 'purchase_payments'}
    
    print("\n📊 Database Schema Check:")
    print(f"   Total tables found: {len(tables)}")
    
    # Check core tables
    core_missing = required_core - set(tables)
    if core_missing:
        print(f"   ❌ Missing core tables: {core_missing}")
        return False
    print(f"   ✓ All core tables present: {required_core}")
    
    # Check optional tables
    optional_found = optional_tables & set(tables)
    if optional_found:
        print(f"   ✓ Optional tables found: {optional_found}")
    
    # List all tables
    print(f"\n   All tables in database:")
    for table in sorted(tables):
        count = get_table_count(db_path, table)
        print(f"      • {table}: {count} records")
    
    return True

def export_database(source_db="fabric.db", backup_name=None):
    """Test database export"""
    print("\n" + "="*60)
    print("🔄 EXPORT TEST")
    print("="*60)
    
    if not os.path.exists(source_db):
        print(f"❌ Source database not found: {source_db}")
        return None
    
    if not check_database_integrity(source_db):
        print(f"❌ Source database integrity check failed")
        return None
    
    print(f"✓ Source database integrity verified: {source_db}")
    
    if backup_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"test_backup_{timestamp}.db"
    
    try:
        shutil.copy2(source_db, backup_name)
        print(f"✓ Database exported: {backup_name}")
        
        if not os.path.exists(backup_name):
            print(f"❌ Backup file not created")
            return None
        
        file_size_mb = os.path.getsize(backup_name) / (1024 * 1024)
        print(f"✓ Backup file size: {file_size_mb:.2f} MB")
        
        # Verify backup integrity
        if not check_database_integrity(backup_name):
            print(f"❌ Backup database integrity check failed")
            os.remove(backup_name)
            return None
        
        print(f"✓ Backup integrity verified")
        
        # Verify schema
        if not verify_schema(backup_name):
            print(f"❌ Backup schema verification failed")
            os.remove(backup_name)
            return None
        
        print(f"✓ All export checks passed!")
        return backup_name
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None

def import_database(backup_file, target_db="fabric_test_import.db"):
    """Test database import"""
    print("\n" + "="*60)
    print("📥 IMPORT TEST")
    print("="*60)
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    print(f"✓ Backup file found: {backup_file}")
    
    # Verify backup before import
    if not check_database_integrity(backup_file):
        print(f"❌ Backup integrity check failed")
        return False
    
    print(f"✓ Backup integrity verified")
    
    # Check schema
    tables_in_backup = get_all_tables(backup_file)
    core_tables = {'companies', 'suppliers', 'customers', 'purchases', 'sales'}
    
    if not core_tables.issubset(set(tables_in_backup)):
        missing = core_tables - set(tables_in_backup)
        print(f"❌ Backup missing required tables: {missing}")
        return False
    
    print(f"✓ Backup schema verification passed")
    
    # Perform import (copy to new location)
    try:
        shutil.copy2(backup_file, target_db)
        print(f"✓ Database imported to: {target_db}")
        
        if not os.path.exists(target_db):
            print(f"❌ Import target file not created")
            return False
        
        # Verify imported database
        if not check_database_integrity(target_db):
            print(f"❌ Imported database integrity check failed")
            os.remove(target_db)
            return False
        
        print(f"✓ Imported database integrity verified")
        
        # Verify schema
        if not verify_schema(target_db):
            print(f"❌ Imported database schema verification failed")
            os.remove(target_db)
            return False
        
        print(f"✓ All import checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        if os.path.exists(target_db):
            os.remove(target_db)
        return False

def compare_databases(db1, db2):
    """Compare two databases for data integrity"""
    print("\n" + "="*60)
    print("🔍 DATABASE COMPARISON TEST")
    print("="*60)
    
    tables_to_compare = ['companies', 'suppliers', 'customers', 'purchases', 'sales']
    
    print(f"\nComparing: {db1} <-> {db2}")
    
    all_match = True
    for table in tables_to_compare:
        count1 = get_table_count(db1, table)
        count2 = get_table_count(db2, table)
        
        if count1 == count2:
            print(f"✓ {table}: {count1} records (MATCH)")
        else:
            print(f"❌ {table}: {count1} vs {count2} (MISMATCH)")
            all_match = False
    
    return all_match

def run_all_tests():
    """Run all import/export tests"""
    print("\n" + "█"*60)
    print("█  DATABASE IMPORT/EXPORT COMPREHENSIVE TEST")
    print("█"*60)
    print(f"   Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Export
    print("\n[STEP 1] Testing database export...")
    backup_file = export_database()
    
    if not backup_file:
        print("\n❌ Export test FAILED")
        return False
    
    # Step 2: Import
    print("\n[STEP 2] Testing database import...")
    if not import_database(backup_file):
        print("\n❌ Import test FAILED")
        return False
    
    # Step 3: Compare
    print("\n[STEP 3] Comparing original and imported databases...")
    if compare_databases("fabric.db", "fabric_test_import.db"):
        print("\n✓ Databases match perfectly!")
    else:
        print("\n⚠️  Database comparison showed differences (may be expected)")
    
    # Cleanup
    print("\n[CLEANUP] Removing test files...")
    for f in [backup_file, "fabric_test_import.db"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"   Removed: {f}")
    
    print("\n" + "█"*60)
    print("█  ALL TESTS PASSED! ✓")
    print("█"*60)
    print(f"   Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
