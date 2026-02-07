from typing import List, Dict, Any, Optional

# Mock cx_Oracle if not available
try:
    import cx_Oracle
    
    class PLSQLExecutor:
        """Executes PL/SQL procedures and functions from Python"""
        
        def __init__(self, connection: cx_Oracle.Connection):
            self.connection = connection
            self.cursor = connection.cursor()
except ImportError:
    # Mock implementation for testing
    class PLSQLExecutor:
        """Mock PL/SQL executor for testing"""
        
        def __init__(self, connection):
            self.connection = connection
            self.cursor = None
    
    def execute_procedure(self, procedure_name: str, parameters: List[Any] = None) -> bool:
        """Execute a PL/SQL procedure"""
        try:
            if parameters:
                bind_vars = [f':{i+1}' for i in range(len(parameters))]
                plsql_block = f"BEGIN {procedure_name}({', '.join(bind_vars)}); END;"
                self.cursor.execute(plsql_block, parameters)
            else:
                plsql_block = f"BEGIN {procedure_name}; END;"
                self.cursor.execute(plsql_block)
            
            self.connection.commit()
            return True
        except cx_Oracle.DatabaseError as e:
            print(f"Procedure execution failed: {e}")
            self.connection.rollback()
            return False
    
    def execute_function(self, function_name: str, parameters: List[Any] = None, 
                        return_type: str = None) -> Optional[Any]:
        """Execute a PL/SQL function and return result"""
        try:
            if parameters:
                bind_vars = [f':{i+1}' for i in range(len(parameters))]
                if return_type:
                    plsql_block = f"SELECT {function_name}({', '.join(bind_vars)}) FROM DUAL"
                    self.cursor.execute(plsql_block, parameters)
                    result = self.cursor.fetchone()
                    return result[0] if result else None
                else:
                    plsql_block = f"BEGIN :result := {function_name}({', '.join(bind_vars)}); END;"
                    result_var = self.cursor.var(cx_Oracle.STRING)
                    self.cursor.execute(plsql_block, parameters + [result_var])
                    return result_var.getvalue()
            else:
                if return_type:
                    plsql_block = f"SELECT {function_name}() FROM DUAL"
                    self.cursor.execute(plsql_block)
                    result = self.cursor.fetchone()
                    return result[0] if result else None
                else:
                    plsql_block = "BEGIN :result := {function_name}(); END;"
                    result_var = self.cursor.var(cx_Oracle.STRING)
                    self.cursor.execute(plsql_block, [result_var])
                    return result_var.getvalue()
        except cx_Oracle.DatabaseError as e:
            print(f"Function execution failed: {e}")
            return None
    
    def execute_dynamic_sql(self, sql_query: str, parameters: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute dynamic SQL and return results as dictionaries"""
        try:
            if parameters:
                self.cursor.execute(sql_query, parameters)
            else:
                self.cursor.execute(sql_query)
            
            columns = [desc[0] for desc in self.cursor.description]
            results = []
            
            for row in self.cursor:
                results.append(dict(zip(columns, row)))
            
            return results
        except cx_Oracle.DatabaseError as e:
            print(f"Dynamic SQL execution failed: {e}")
            return []
    
    def close(self):
        """Close cursor and connection"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()