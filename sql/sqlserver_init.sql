-- SQL Server Database Initialization Script
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

CREATE TABLE local_employees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    oracle_employee_id INT,
    local_name NVARCHAR(100),
    local_department NVARCHAR(50)
);

-- Insert sample data
INSERT INTO departments VALUES (1, 'IT', 'New York');
INSERT INTO departments VALUES (2, 'Finance', 'London');
INSERT INTO departments VALUES (3, 'HR', 'Tokyo');

INSERT INTO employees VALUES (101, N'John Doe', N'IT', 75000.00, '2020-01-15');
INSERT INTO employees VALUES (102, N'Jane Smith', N'Finance', 85000.00, '2019-03-20');
INSERT INTO employees VALUES (103, N'Bob Johnson', N'HR', 65000.00, '2021-06-10');
INSERT INTO employees VALUES (104, N'Alice Brown', N'IT', 90000.00, '2018-11-05');

INSERT INTO local_employees VALUES (101, N'John Doe Local', N'IT Support');
INSERT INTO local_employees VALUES (102, N'Jane Smith Local', N'Finance Analysis');
INSERT INTO local_employees VALUES (103, N'Bob Johnson Local', N'HR Administration');
INSERT INTO local_employees VALUES (104, N'Alice Brown Local', N'IT Development');

GO