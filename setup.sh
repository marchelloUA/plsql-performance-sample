#!/bin/bash

# Setup script for PL/SQL Performance Sample Project
echo "Setting up PL/SQL Performance Sample Project..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Start databases
echo "Starting databases..."
docker-compose up -d

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 30

# Check if Oracle is ready
echo "Checking Oracle database..."
until docker exec oracle-free sqlplus -s sys/YourPassword123@localhost:1521/FREEPDB1 as sysdba @sql/oracle_init.sql; do
    echo "Waiting for Oracle to be ready..."
    sleep 10
done

# Check if SQL Server is ready
echo "Checking SQL Server database..."
until docker exec sql-server /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword123!' -Q "CREATE DATABASE temp_db;"; do
    echo "Waiting for SQL Server to be ready..."
    sleep 10
done

# Initialize SQL Server database
echo "Initializing SQL Server database..."
docker exec sql-server /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword123!' -i sql/sqlserver_init.sql

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "Database connections:"
echo "Oracle: localhost:1521 (service: FREEPDB1, user: plsql_dev, password: DevPassword123)"
echo "SQL Server: localhost:1433 (user: sa, password: YourStrongPassword123!)"
echo ""
echo "To test connections:"
echo "python python/database/connection_oracle.py"
echo "python python/database/connection_sqlserver.py"
echo ""
echo "To test cross-database queries:"
echo "python python/cross_database/cross_database_query.py"
echo ""
echo "To test Windows authentication:"
echo "python python/windows_auth/windows_auth_example.py"
echo ""
echo "To run PowerShell script:"
echo "pwsh windows_script.ps1"