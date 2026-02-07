import getpass

# Mock pyodbc if not available
try:
    import pyodbc
    
    def connect_windows_auth():
        """Connect using Windows authentication"""
        try:
            # Windows authentication connection string
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost,1434;"
                "DATABASE=master;"
                "Trusted_Connection=yes;"
                "Authentication=ActiveDirectoryIntegrated;"
            )
            
            connection = pyodbc.connect(conn_str)
            print("Windows authentication successful!")
            return connection
            
        except pyodbc.Error as e:
            print(f"Windows authentication failed: {e}")
            print("Falling back to SQL authentication...")
            
            # Fallback to SQL authentication
            conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost,1434;"
                "DATABASE=master;"
                "UID=sa;"
                "PWD=YourStrongPassword123!"
            )
            
            return pyodbc.connect(conn_str)
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
            return ["MockUser", "MockDB"]
        def close(self):
            pass
    
    def connect_windows_auth():
        """Mock Windows authentication for testing"""
        print("Mock Windows authentication (pyodbc not available)")
        return MockConnection()

# Test connection
conn = connect_windows_auth()
cursor = conn.cursor()
cursor.execute("SELECT SYSTEM_USER, USER")
print(f"Connected as: {cursor.fetchone()}")
cursor.close()
conn.close()