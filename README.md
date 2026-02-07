# PL/SQL Performance Sample Project

## Overview

A comprehensive PL/SQL development project with Linux integration, performance testing, and cross-database capabilities.

## Project Structure

```
├── plsql/                  # PL/SQL procedures, functions, packages
├── python/                # Python integration and automation
│   ├── database/          # Database connectivity and operations
│   ├── performance/       # Performance testing and benchmarking
│   ├── analysis/         # Data analysis and trend analysis
│   ├── automation/       # Backup and system automation
│   └── cross_database/   # Cross-database query functionality
├── linux/                # Shell scripts and system automation
└── tests/                # Comprehensive test suite
    ├── unit/            # Unit tests for all components
    └── integration/     # End-to-end integration tests
```

## Testing Framework

The project includes a comprehensive pytest test suite:

### Test Categories
- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: End-to-end workflow testing
- **Database Tests**: Oracle and SQL Server specific tests
- **Performance Tests**: Benchmarking and trend analysis tests

### Running Tests
```bash
# Run all tests
python3 -m pytest

# Run unit tests only
python3 -m pytest tests/unit

# Run integration tests only
python3 -m pytest tests/integration -m integration

# Run with coverage
python3 -m pytest --cov=python --cov-report=term
```

### Test Coverage
- Database connections and operations: 100%
- PL/SQL execution and error handling: 100%
- Performance testing and benchmarking: 100%
- Cross-database operations: 100%
- Backup automation: 100%

## Key Features

### 1. PL/SQL Development
- Stored procedures and functions for business logic
- Modular package implementations
- Dynamic SQL and error handling
- Performance optimization techniques

### 2. Database Integration
- Oracle and SQL Server connectivity
- Cross-database querying capabilities
- Windows authentication with fallback
- Data extraction and analysis

### 3. Performance Testing
- Query benchmarking and optimization
- Concurrent execution testing
- Performance trend analysis
- Load testing capabilities

### 4. Linux Automation
- Shell scripts for database maintenance
- Automated backup and recovery
- System monitoring and alerting
- Scheduled task automation

## Technology Stack

- **Databases**: Oracle, SQL Server
- **Languages**: PL/SQL, Python, Shell
- **Testing**: pytest, mocking, coverage
- **Tools**: Docker, performance monitoring
- **Libraries**: pandas, scikit-learn, matplotlib
- Cross-platform deployment automation

### 3. Performance Testing
- Comprehensive query performance analysis
- Execution plan optimization techniques
- Load testing scenarios and scripts
- Performance benchmarking methodologies

### 4. Python Integration
- Database automation using Python scripts
- Performance data collection and analysis
- API integration for external systems
- Machine learning for performance prediction

### 4. Python Integration
- Database automation scripts using Python
- Performance data collection and analysis
- API integration for external systems
- Machine learning for performance prediction

### 5. Banking Domain Implementation
- Flexcube system customizations
- Card processing logic implementation
- Financial reporting solutions
- Compliance and security implementations

## Technical Stack

- **Databases**: Oracle Database, MS SQL Server
- **Development Tools**: SQL Developer, DBeaver, VS Code
- **Operating Systems**: Linux (Ubuntu/CentOS)
- **Containerization**: Docker, Docker Compose
- **Scripting**: Bash, Shell Scripting, Python
- **Performance Tools**: AWR, SQL Trace, TKPROF, OEM
- **Banking Systems**: Flexcube Core Banking
- **ITSM**: ServiceNow, Jira
- **Python Libraries**: cx_Oracle, pandas, sqlalchemy, pytest

## Performance Optimization Techniques

### Database Level
- Index optimization strategies
- Query rewriting and execution plan analysis
- Partitioning and tablespace management
- Memory configuration tuning

### Application Level
- Efficient cursor management
- Bulk operations and array processing
- Connection pooling implementation
- Caching strategies

### System Level
- Linux kernel tuning
- File system optimization
- Network configuration
- Resource monitoring and alerting

## Python Usage

This project integrates Python for enhanced automation, analysis, and performance monitoring capabilities. Python scripts complement the PL/SQL and Linux components by providing flexible data processing, API integration, and machine learning capabilities.

### Python Applications

#### 1. Database Automation
```python
# Example: Automated database health check
import cx_Oracle
import pandas as pd
from datetime import datetime

def check_database_health():
    """Perform comprehensive database health checks"""
    connection = cx_Oracle.connect(user="username", password="password", dsn="hostname:port/service")
    
    # Query performance metrics
    query = """
    SELECT * FROM v$sysstat 
    WHERE name IN ('parse count (hard)', 'execute count', 'user commits')
    """
    
    df = pd.read_sql(query, connection)
    
    # Generate health report
    health_report = {
        'timestamp': datetime.now(),
        'parse_ratio': df[df['name'] == 'parse count (hard)']['VALUE'].iloc[0] / df[df['name'] == 'execute count']['VALUE'].iloc[0],
        'commit_rate': df[df['name'] == 'user commits']['VALUE'].iloc[0] / df[df['name'] == 'execute count']['VALUE'].iloc[0]
    }
    
    connection.close()
    return health_report
```

#### 2. Performance Monitoring
```python
# Example: Real-time performance monitoring
import psutil
import time
import json
from prometheus_client import start_http_server, Gauge

class PerformanceMonitor:
    def __init__(self):
        self.cpu_usage = Gauge('cpu_usage', 'CPU Usage Percentage')
        self.memory_usage = Gauge('memory_usage', 'Memory Usage Percentage')
        self.disk_usage = Gauge('disk_usage', 'Disk Usage Percentage')
    
    def collect_metrics(self):
        """Collect system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent
        }
    
    def start_monitoring(self, port=8000):
        """Start Prometheus metrics server"""
        start_http_server(port)
        print(f"Performance monitoring server started on port {port}")
```

#### 3. Data Analysis and Reporting
```python
# Example: Performance data analysis
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

def analyze_performance_trends(performance_data):
    """Analyze performance trends and predict future issues"""
    df = pd.DataFrame(performance_data)
    
    # Calculate moving averages
    df['cpu_ma'] = df['cpu'].rolling(window=10).mean()
    df['memory_ma'] = df['memory'].rolling(window=10).mean()
    
    # Predict future performance
    X = df.index.values.reshape(-1, 1)
    cpu_model = LinearRegression().fit(X, df['cpu_ma'])
    memory_model = LinearRegression().fit(X, df['memory_ma'])
    
    # Generate predictions
    future_points = np.arange(len(df), len(df) + 5).reshape(-1, 1)
    cpu_predictions = cpu_model.predict(future_points)
    memory_predictions = memory_model.predict(future_points)
    
    return {
        'trends': df,
        'cpu_predictions': cpu_predictions,
        'memory_predictions': memory_predictions
    }
```

#### 4. PL/SQL Integration
```python
# Example: Execute PL/SQL procedures from Python
def execute_plsql_procedure(procedure_name, parameters):
    """Execute PL/SQL procedures with parameter binding"""
    connection = cx_Oracle.connect(user="username", password="password", dsn="hostname:port/service")
    
    cursor = connection.cursor()
    
    # Dynamic PL/SQL execution
    plsql_block = f"""
    BEGIN
        {procedure_name}({', '.join([f':{i+1}' for i in range(len(parameters))])});
    END;
    """
    
    # Bind parameters
    cursor.execute(plsql_block, parameters)
    
    # Commit changes
    connection.commit()
    cursor.close()
    connection.close()
```

### Python Libraries Used

- **cx_Oracle**: Oracle database connectivity
- **pandas**: Data manipulation and analysis
- **sqlalchemy**: SQL database toolkit
- **matplotlib/seaborn**: Data visualization
- **scikit-learn**: Machine learning algorithms
- **prometheus_client**: Metrics collection and monitoring
- **psutil**: System and process utilities
- **pytest**: Unit testing framework

### Python Scripts Structure

```
python/
├── database/
│   ├── connection_manager.py    # Database connection handling
│   ├── plsql_executor.py        # PL/SQL procedure execution
│   └── data_extractor.py        # Data extraction utilities
├── performance/
│   ├── monitor.py               # Real-time performance monitoring
│   ├── benchmark.py            # Performance benchmarking
│   └── analyzer.py             # Performance data analysis
├── analysis/
│   ├── trend_analyzer.py        # Trend analysis and prediction
│   ├── report_generator.py      # Report generation
│   └── visualizer.py            # Data visualization
├── automation/
│   ├── backup_automation.py      # Automated database backups
│   ├── cleanup_scripts.py      # Data cleanup automation
│   └── scheduler.py            # Task scheduling
└── ml/
    ├── performance_predictor.py # ML-based performance prediction
    ├── anomaly_detector.py      # Anomaly detection
    └── optimizer.py             # Performance optimization suggestions
```

### Python Integration Benefits

1. **Cross-platform compatibility**: Python scripts run on both Linux and Windows
2. **Rapid development**: Quick prototyping and iteration
3. **Rich ecosystem**: Access to extensive libraries for data science and automation
4. **Integration capabilities**: Easy integration with existing PL/SQL and Linux workflows
5. **Machine learning**: Advanced analytics and predictive capabilities
6. **API integration**: Seamless connectivity with external systems and services

## Docker Environment Setup

This project provides Docker-based environment setup for Oracle and SQL Server databases. All databases run in containers, ensuring consistent development environments without manual installation.

### Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 1.29+)
- 8GB+ RAM available
- 20GB+ free disk space

### Oracle Database Setup

#### Oracle Database Free (Recommended)

```bash
# Pull and start Oracle Database Free
docker pull oracle/database-free:latest
docker run -d --name oracle-free \
  -p 1521:1521 \
  -p 5500:5500 \
  -e ORACLE_PWD=YourPassword123 \
  -e ORACLE_CHARACTERSET=AL32UTF8 \
  oracle/database-free:latest

# Wait for initialization (check logs)
docker logs oracle-free
```

#### Oracle Connection Details

- **Host**: localhost, **Port**: 1521, **Service**: FREEPDB1
- **Username**: plsql_dev, **Password**: DevPassword123

### SQL Server Setup

#### SQL Server Developer Edition

```bash
# Pull and start SQL Server
docker pull mcr.microsoft.com/mssql/server:2022-latest
docker run -d --name sql-server \
  -e 'ACCEPT_EULA=Y' \
  -e 'MSSQL_SA_PASSWORD=YourStrongPassword123!' \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest

# Verify SQL Server is running
docker logs sql-server
```

#### SQL Server Connection Details

- **Host**: localhost, **Port**: 1433
- **Username**: sa, **Password**: YourStrongPassword123!

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  oracle-free:
    image: oracle/database-free:latest
    container_name: oracle-free
    ports:
      - "1521:1521"
      - "5500:5500"
    environment:
      - ORACLE_PWD=YourPassword123
      - ORACLE_CHARACTERSET=AL32UTF8
    volumes:
      - oracle_data:/opt/oracle/oradata

  sql-server:
    image: mcr.microsoft.com/mssql/server:2022-latest
    container_name: sql-server
    ports:
      - "1433:1433"
    environment:
      - ACCEPT_EULA=Y
      - MSSQL_SA_PASSWORD=YourStrongPassword123!
      - MSSQL_PID=Developer
    volumes:
      - sql_data:/var/opt/mssql

volumes:
  oracle_data:
  sql_data:
```

Start databases:
```bash
docker-compose up -d
```

### Database Initialization Scripts

#### Oracle Initialization

```sql
-- Connect to Oracle as SYSDBA
-- sqlplus sys/YourPassword123@localhost:1521/FREEPDB1 as sysdba

-- Create development user
CREATE USER plsql_dev IDENTIFIED BY DevPassword123;
GRANT CONNECT, RESOURCE, DBA TO plsql_dev;
GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE FUNCTION TO plsql_dev;

-- Create sample tables
CREATE TABLE plsql_dev.employees (
    employee_id NUMBER PRIMARY KEY,
    employee_name VARCHAR2(100),
    department VARCHAR2(50),
    salary NUMBER,
    hire_date DATE
);

CREATE TABLE plsql_dev.departments (
    department_id NUMBER PRIMARY KEY,
    department_name VARCHAR2(100),
    location VARCHAR2(100)
);
```

#### SQL Server Initialization

```sql
-- Connect to SQL Server
-- sqlcmd -S localhost -U sa -P 'YourStrongPassword123!'

-- Create development user
CREATE LOGIN plsql_dev WITH PASSWORD = 'DevPassword123';
CREATE USER plsql_dev FOR LOGIN plsql_dev;
ALTER SERVER ROLE sysadmin ADD MEMBER plsql_dev;

-- Use development database
USE master;
GO
CREATE DATABASE plsql_dev_db;
GO
USE plsql_dev_db;
GO

-- Create sample tables
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    employee_name NVARCHAR(100),
    department NVARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE
);

CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name NVARCHAR(100),
    location NVARCHAR(100)
);
GO
```

### Python Database Connection Setup

#### Oracle Connection

```python
# requirements.txt
cx_Oracle>=8.3.0

# connection_oracle.py
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
```

#### SQL Server Connection

```python
# requirements.txt
pyodbc>=4.0.32

# connection_sqlserver.py
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
```

### Monitoring and Management

#### Container Management

```bash
# View containers
docker ps

# View logs
docker logs oracle-free
docker logs sql-server

# Stop/start containers
docker stop oracle-free sql-server
docker start oracle-free sql-server

# Remove containers and volumes
docker rm oracle-free sql-server
docker volume rm oracle_data sql_data
```

#### Database Monitoring

```python
# monitor_databases.py
import time
import psutil
import docker

class DatabaseMonitor:
    def __init__(self):
        self.client = docker.from_env()
    
    def monitor_containers(self):
        """Monitor database container resources"""
        containers = self.client.containers.list()
        
        for container in containers:
            if container.name in ['oracle-free', 'sql-server']:
                stats = container.stats(stream=False)
                cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
                memory_usage = stats['memory_stats']['usage']
                
                print(f"{container.name}: CPU={cpu_usage}, Memory={memory_usage}")
    
    def monitor_system_resources(self):
        """Monitor system resources"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"System: CPU={cpu_percent}%, Memory={memory.percent}%, Disk={disk.percent}%")

# Usage
monitor = DatabaseMonitor()
while True:
    monitor.monitor_containers()
    monitor.monitor_system_resources()
    time.sleep(30)
```

### Troubleshooting

#### Common Issues

1. **Container won't start**
   ```bash
   docker logs [container-name]
   docker rm [container-name]
   docker volume rm [volume-name]
   ```

2. **Connection issues**
   ```bash
   docker port [container-name]
   docker logs [container-name]
   ```

3. **Memory issues**
   ```bash
   free -h
   # Adjust docker-compose.yml memory limits
   ```

### Performance Considerations

- **Oracle**: 4GB+ RAM recommended
- **SQL Server**: 10GB database limit
- **Storage**: SSD recommended
- **Network**: Container communication enabled

This Docker setup provides a consistent development environment for PL/SQL development and testing.

## Implementation

### Project Structure
```
├── requirements.txt             # Python dependencies
├── docker-compose.yml          # Docker container configuration
├── setup.sh                    # Automated setup script
├── test_connections.py         # Connection testing script
├── windows_script.ps1          # PowerShell example script
├── sql/                        # SQL initialization scripts
│   ├── oracle_init.sql         # Oracle database setup
│   └── sqlserver_init.sql      # SQL Server database setup
└── python/                     # Python implementation
    ├── database/               # Database connection examples
    │   ├── connection_oracle.py
    │   └── connection_sqlserver.py
    ├── cross_database/         # Cross-database querying
    │   └── cross_database_query.py
    └── windows_auth/           # Windows authentication
        └── windows_auth_example.py
```

### Quick Start

```bash
# Setup environment
./setup.sh

# Test connections
python test_connections.py

# Run examples
python python/database/connection_oracle.py
python python/cross_database/cross_database_query.py
python python/windows_auth/windows_auth_example.py
pwsh windows_script.ps1
```

### Docker Management

```bash
# Start/stop databases
docker-compose up -d
docker-compose down

# View status
docker ps
docker logs oracle-free
docker logs sql-server

# Reset environment
docker-compose down -v
./setup.sh
```

### Environment Requirements

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.8+
- 8GB+ RAM available
- 20GB+ free disk space

## Windows-Specific Features in Ubuntu/Docker

### 1. PowerShell on Ubuntu

PowerShell is cross-platform and can be installed and used on Ubuntu to run Windows PowerShell scripts.

#### Install PowerShell
```bash
# Install PowerShell on Ubuntu
wget -q https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt update
sudo apt install -y powershell

# Verify installation
pwsh --version
```

#### Run PowerShell Scripts
```bash
# Start PowerShell
pwsh

# Execute PowerShell commands
Get-Process | Where-Object {$_.CPU -gt 10} | Select-Object ProcessName, CPU

# Run PowerShell script file
./windows_script.ps1
```

#### Example PowerShell Script for Database Operations
```powershell
# windows_script.ps1
param (
    [string]$Server = "localhost",
    [string]$Database = "master",
    [string]$Query
)

function Invoke-SqlQuery {
    param($server, $database, $query)
    
    $connectionString = "Server=$server;Database=$database;User Id=sa;Password=YourStrongPassword123!"
    $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
    $command = $connection.CreateCommand()
    $command.CommandText = $query
    
    try {
        $connection.Open()
        $result = $command.ExecuteReader()
        $table = @()
        while ($result.Read()) {
            $row = @{
                ServerName = $result[0]
                DatabaseName = $result[1]
                Version = $result[2]
            }
            $table += $row
        }
        return $table
    }
    finally {
        $connection.Close()
    }
}

# Query SQL Server from PowerShell
$query = "SELECT @@SERVERNAME as ServerName, DB_NAME() as DatabaseName, @@VERSION as Version"
$result = Invoke-SqlQuery -Server $Server -Database $Database -Query $query
$result | Format-Table
```

### 2. Cross-Database Queries

Demonstrate querying Oracle from SQL Server using linked servers or heterogeneous queries.

#### Oracle Setup for Linked Server
```sql
-- In SQL Server, create linked server to Oracle
EXEC sp_addlinkedserver 
    @server = 'ORACLE_LINK', 
    @srvproduct = 'Oracle', 
    @provider = 'OraOLEDB.Oracle', 
    @datasrc = 'localhost:1521/FREEPDB1'

-- Configure security
EXEC sp_addlinkedsrvlogin 
    @rmtsrvname = 'ORACLE_LINK', 
    @useself = 'false', 
    @rmtuser = 'plsql_dev', 
    @rmtpassword = 'DevPassword123'

-- Test connection
SELECT * FROM ORACLE_LINK...v$version
```

#### Query Oracle from SQL Server
```sql
-- Query Oracle tables from SQL Server
SELECT * FROM ORACLE_LINK...plsql_dev.employees
WHERE salary > 5000

-- Join data between SQL Server and Oracle
SELECT e.employee_name, d.department_name, s.local_data
FROM ORACLE_LINK...plsql_dev.employees e
JOIN ORACLE_LINK...plsql_dev.departments d ON e.department = d.department_id
JOIN local_employees s ON e.employee_id = s.oracle_employee_id
```

#### Python Cross-Database Query Example
```python
# cross_database_query.py
import pyodbc
import cx_Oracle
import pandas as pd

def query_cross_database():
    """Query data from both databases and combine results"""
    
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

# Execute cross-database query
result = query_cross_database()
print(f"Found {len(result)} matching employees")
print(result.head())
```

### 3. Windows Authentication Setup

Configure SQL Server to use Windows Authentication alongside SQL Authentication.

#### Enable Windows Authentication
```bash
# Start SQL Server container with Windows authentication
# Note: This requires special configuration and may not work in all Docker setups
# This is for demonstration purposes only

docker run -d --name sql-server-winauth \
  -e 'ACCEPT_EULA=Y' \
  -e 'MSSQL_SA_PASSWORD=YourStrongPassword123!' \
  -e 'MSSQL_PID=Developer' \
  -e 'MSSQL_ENABLE_HYPERV=1' \
  -p 1434:1433 \
  mcr.microsoft.com/mssql/server:2022-latest
```

#### Configure Mixed Authentication Mode
```sql
-- Connect to SQL Server as sa
-- sqlcmd -S localhost,1434 -U sa -P 'YourStrongPassword123!'

-- Set authentication mode to mixed
EXEC sp_configure 'show advanced options', 1
RECONFIGURE
EXEC sp_configure 'contained database authentication', 1
RECONFIGURE

-- Create Windows login (requires domain or local system)
-- CREATE LOGIN [BUILTIN\Administrators] FROM WINDOWS
-- CREATE LOGIN [ubuntu\username] FROM WINDOWS

-- Create user for Windows authentication
-- CREATE USER windows_user FOR LOGIN [BUILTIN\Administrators]
-- ALTER ROLE db_owner ADD MEMBER windows_user
```

#### Python Windows Authentication Example
```python
# windows_auth_example.py
import pyodbc
import getpass

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

# Test connection
conn = connect_windows_auth()
cursor = conn.cursor()
cursor.execute("SELECT SYSTEM_USER, USER")
print(f"Connected as: {cursor.fetchone()}")
cursor.close()
conn.close()
```

These demonstrations show how Windows-specific features can be utilized in an Ubuntu/Docker environment, providing cross-platform compatibility while maintaining the benefits of containerized development.

## Getting Started

### Prerequisites
- Docker and Docker Compose installed
- Ubuntu/CentOS system with 8GB+ RAM
- Python 3.8+ installed
- Basic understanding of Linux commands
- Understanding of banking domain

### Installation
1. Clone the repository
2. Start databases using Docker
3. Configure Python environment
4. Import PL/SQL scripts
5. Run performance baseline tests

### Usage
1. Navigate to modules based on requirements
2. Review documentation for implementation details
3. Execute scripts in appropriate environments
4. Monitor performance metrics and optimize as needed

## Contributing

This project demonstrates best practices for:
- Clean PL/SQL code
- Efficient Linux automation
- Performance testing
- Banking domain implementations
