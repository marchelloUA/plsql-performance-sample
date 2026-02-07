-- Oracle Database Initialization Script
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

-- Insert sample data
INSERT INTO plsql_dev.departments VALUES (1, 'IT', 'New York');
INSERT INTO plsql_dev.departments VALUES (2, 'Finance', 'London');
INSERT INTO plsql_dev.departments VALUES (3, 'HR', 'Tokyo');

INSERT INTO plsql_dev.employees VALUES (101, 'John Doe', 'IT', 75000, TO_DATE('2020-01-15', 'YYYY-MM-DD'));
INSERT INTO plsql_dev.employees VALUES (102, 'Jane Smith', 'Finance', 85000, TO_DATE('2019-03-20', 'YYYY-MM-DD'));
INSERT INTO plsql_dev.employees VALUES (103, 'Bob Johnson', 'HR', 65000, TO_DATE('2021-06-10', 'YYYY-MM-DD'));
INSERT INTO plsql_dev.employees VALUES (104, 'Alice Brown', 'IT', 90000, TO_DATE('2018-11-05', 'YYYY-MM-DD'));

COMMIT;