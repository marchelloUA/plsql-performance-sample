# Mock cx_Oracle if not available
try:
    import cx_Oracle
    
    def create_oracle_connection():
        """Create connection to Oracle database"""
        dsn = cx_Oracle.makedsn("localhost", 1521, service_name="FREEPDB1")
        return cx_Oracle.connect(
            user="plsql_dev",
            password="DevPassword123",
            dsn=dsn,
            encoding="UTF-8"
        )
    
    # Test connection
    try:
        conn = create_oracle_connection()
        print("Oracle connection successful!")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM v$version")
        print(f"Oracle version: {cursor.fetchone()[0]}")
        cursor.close()
        conn.close()
    except cx_Oracle.DatabaseError as e:
        print(f"Oracle connection error: {e}")
        
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
            return ["Oracle Mock Version"]
        def close(self):
            pass
    
    def create_oracle_connection():
        """Mock Oracle connection for testing"""
        print("Mock Oracle connection (cx_Oracle not available)")
        return MockConnection()