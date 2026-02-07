# Mock pyodbc if not available
try:
    import pyodbc
    
    def create_sqlserver_connection():
        """Create connection to SQL Server database"""
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=plsql_dev_db;"
            "UID=sa;"
            "PWD=YourStrongPassword123!"
        )
        return pyodbc.connect(conn_str)
    
    # Test connection
    try:
        conn = create_sqlserver_connection()
        print("SQL Server connection successful!")
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        print(f"SQL Server version: {cursor.fetchone()[0]}")
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print(f"SQL Server connection error: {e}")
        
except ImportError:
    # Mock implementation for testing
    class MockConnection:
        def cursor(self):
            return MockCursor()
        def close(self):
            pass
    
    class MockCursor:
        def execute(self, query):
            pass
        def fetchone(self):
            return ["SQL Server Mock Version"]
        def close(self):
            pass
    
    def create_sqlserver_connection():
        """Mock SQL Server connection for testing"""
        print("Mock SQL Server connection (pyodbc not available)")
        return MockConnection()