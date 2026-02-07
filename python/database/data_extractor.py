import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from unittest.mock import Mock

# Mock cx_Oracle if not available
try:
    import cx_Oracle
    
    class DataExtractor:
        """Extracts data from Oracle database for analysis"""
        
        def __init__(self, connection: cx_Oracle.Connection):
            self.connection = connection
except ImportError:
    # Mock implementation for testing
    class DataExtractor:
        """Mock data extractor for testing"""
        
        def __init__(self, connection):
            self.connection = connection
    
    def extract_table_data(self, table_name: str, schema: str = "plsql_dev", 
                          conditions: str = None) -> pd.DataFrame:
        """Extract data from a specific table"""
        try:
            query = f"SELECT * FROM {schema}.{table_name}"
            if conditions:
                query += f" WHERE {conditions}"
            
            df = pd.read_sql(query, self.connection)
            return df
        except Exception as e:
            print(f"Data extraction failed: {e}")
            return pd.DataFrame()
    
    def extract_performance_metrics(self) -> pd.DataFrame:
        """Extract database performance metrics"""
        try:
            query = """
            SELECT s.name, s.value 
            FROM v$sysstat s 
            WHERE s.name IN ('parse count (hard)', 'execute count', 'user commits', 'db block gets')
            """
            
            df = pd.read_sql(query, self.connection)
            
            # Calculate derived metrics
            if len(df) >= 2:
                parse_hard = df[df['name'] == 'parse count (hard)']['value'].iloc[0]
                execute_count = df[df['name'] == 'execute count']['value'].iloc[0]
                commit_count = df[df['name'] == 'user commits']['value'].iloc[0]
                
                df['parse_ratio'] = parse_hard / execute_count if execute_count > 0 else 0
                df['commit_ratio'] = commit_count / execute_count if execute_count > 0 else 0
            
            return df
        except Exception as e:
            print(f"Performance metrics extraction failed: {e}")
            return pd.DataFrame()
    
    def extract_wait_events(self, top_n: int = 10) -> pd.DataFrame:
        """Extract top wait events"""
        try:
            query = f"""
            SELECT event, total_waits, time_waited, average_wait
            FROM v$system_event
            WHERE wait_class != 'Idle'
            ORDER BY time_waited DESC
            FETCH FIRST {top_n} ROWS ONLY
            """
            
            return pd.read_sql(query, self.connection)
        except Exception as e:
            print(f"Wait events extraction failed: {e}")
            return pd.DataFrame()
    
    def extract_tablespace_usage(self) -> pd.DataFrame:
        """Extract tablespace usage information"""
        try:
            query = """
            SELECT tablespace_name, ROUND(used_space * 8 / 1024, 2) as used_gb,
                   ROUND(tablespace_size * 8 / 1024, 2) as total_gb,
                   ROUND((used_space / tablespace_size) * 100, 2) as usage_percent
            FROM dba_tablespace_usage_metrics
            ORDER BY usage_percent DESC
            """
            
            return pd.read_sql(query, self.connection)
        except Exception as e:
            print(f"Tablespace usage extraction failed: {e}")
            return pd.DataFrame()
    
    def extract_session_info(self) -> pd.DataFrame:
        """Extract active session information"""
        try:
            query = """
            SELECT s.sid, s.serial#, s.username, s.status, s.last_call_et,
                   s.blocking_session, s.wait_class, s.wait_event
            FROM v$session s
            WHERE s.username IS NOT NULL
            ORDER BY s.last_call_et DESC
            """
            
            return pd.read_sql(query, self.connection)
        except Exception as e:
            print(f"Session info extraction failed: {e}")
            return pd.DataFrame()
    
    def extract_to_csv(self, data: pd.DataFrame, filename: str) -> bool:
        """Extract data to CSV file"""
        try:
            data.to_csv(filename, index=False)
            return True
        except Exception as e:
            print(f"CSV export failed: {e}")
            return False
    
    def extract_to_json(self, data: pd.DataFrame, filename: str) -> bool:
        """Extract data to JSON file"""
        try:
            data.to_json(filename, orient='records', indent=2)
            return True
        except Exception as e:
            print(f"JSON export failed: {e}")
            return False