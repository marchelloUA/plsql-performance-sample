#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python', 'database'))

from connection_oracle import create_oracle_connection
from connection_sqlserver import create_sqlserver_connection
import subprocess

def test_oracle_connection():
    """Test Oracle database connection"""
    print("Testing Oracle connection...")
    try:
        conn = create_oracle_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 'Oracle connection successful!' FROM DUAL")
        result = cursor.fetchone()
        print(f"✓ {result[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Oracle connection failed: {e}")
        return False

def test_sqlserver_connection():
    """Test SQL Server database connection"""
    print("Testing SQL Server connection...")
    try:
        conn = create_sqlserver_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 'SQL Server connection successful!'")
        result = cursor.fetchone()
        print(f"✓ {result[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ SQL Server connection failed: {e}")
        return False

def test_powershell():
    """Test PowerShell script"""
    print("Testing PowerShell script...")
    try:
        result = subprocess.run(['pwsh', 'windows_script.ps1'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ PowerShell script executed successfully")
            return True
        else:
            print(f"✗ PowerShell script failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ PowerShell test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running connection tests...")
    print("=" * 50)
    
    results = []
    results.append(test_oracle_connection())
    results.append(test_sqlserver_connection())
    results.append(test_powershell())
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} out of {total} tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())