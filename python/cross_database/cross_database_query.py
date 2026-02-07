import pandas as pd
from unittest.mock import Mock

# Mock database modules if not available
try:
    import pyodbc
except ImportError:
    pyodbc = Mock()

try:
    import cx_Oracle
except ImportError:
    cx_Oracle = Mock()

def query_cross_database():
    """Query data from both databases and combine results"""
    
    try:
        # Query SQL Server
        sql_conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=plsql_dev_db;"
            "UID=sa;PWD=YourStrongPassword123!"
        )
        
        sql_query = "SELECT * FROM local_employees"
        sql_df = pd.read_sql(sql_query, sql_conn)
        
        # Query Oracle
        oracle_dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREEPDB1")
        oracle_conn = cx_Oracle.connect(
            user="plsql_dev",
            password="DevPassword123",
            dsn=oracle_dsn
        )
        
        oracle_query = "SELECT * FROM plsql_dev.employees"
        oracle_df = pd.read_sql(oracle_query, oracle_conn)
        
        # Combine results
        combined_df = pd.merge(
            oracle_df, 
            sql_df, 
            left_on="employee_id", 
            right_on="oracle_employee_id", 
            how="inner"
        )
        
        return combined_df
    except Exception as e:
        print(f"Cross-database query failed: {e}")
        return pd.DataFrame()

# Execute cross-database query
result = query_cross_database()
print(f"Found {len(result)} matching employees")
print(result.head())