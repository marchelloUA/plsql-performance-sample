-- Employee Management Procedures
-- This file contains stored procedures for employee data management

CREATE OR REPLACE PROCEDURE add_employee(
    p_employee_id IN NUMBER,
    p_employee_name IN VARCHAR2,
    p_department_id IN NUMBER,
    p_salary IN NUMBER,
    p_hire_date IN DATE
)
IS
BEGIN
    -- Insert new employee record
    INSERT INTO plsql_dev.employees (
        employee_id,
        employee_name,
        department,
        salary,
        hire_date
    ) VALUES (
        p_employee_id,
        p_employee_name,
        (SELECT department_name FROM plsql_dev.departments WHERE department_id = p_department_id),
        p_salary,
        p_hire_date
    );
    
    COMMIT;
    
    DBMS_OUTPUT.PUT_LINE('Employee ' || p_employee_name || ' added successfully.');
EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
        DBMS_OUTPUT.PUT_LINE('Error: Employee ID already exists.');
        ROLLBACK;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error adding employee: ' || SQLERRM);
        ROLLBACK;
END add_employee;
/

CREATE OR REPLACE PROCEDURE update_employee_salary(
    p_employee_id IN NUMBER,
    p_new_salary IN NUMBER
)
IS
    v_old_salary NUMBER;
    v_employee_name VARCHAR2(100);
BEGIN
    -- Get current employee details
    SELECT employee_name, salary 
    INTO v_employee_name, v_old_salary
    FROM plsql_dev.employees
    WHERE employee_id = p_employee_id;
    
    -- Update salary
    UPDATE plsql_dev.employees
    SET salary = p_new_salary
    WHERE employee_id = p_employee_id;
    
    COMMIT;
    
    DBMS_OUTPUT.PUT_LINE('Employee ' || v_employee_name || ' salary updated from ' || 
                         v_old_salary || ' to ' || p_new_salary || '.');
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Error: Employee ID ' || p_employee_id || ' not found.');
        ROLLBACK;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error updating salary: ' || SQLERRM);
        ROLLBACK;
END update_employee_salary;
/

CREATE OR REPLACE PROCEDURE get_employee_by_department(
    p_department_id IN NUMBER,
    p_cursor OUT SYS_REFCURSOR
)
IS
BEGIN
    OPEN p_cursor FOR
    SELECT e.employee_id, e.employee_name, e.salary, e.hire_date, d.department_name
    FROM plsql_dev.employees e
    JOIN plsql_dev.departments d ON e.department = d.department_id
    WHERE d.department_id = p_department_id
    ORDER BY e.employee_name;
END get_employee_by_department;
/

CREATE OR REPLACE PROCEDURE calculate_department_budget(
    p_department_id IN NUMBER,
    p_budget OUT NUMBER
)
IS
    v_total_salary NUMBER;
BEGIN
    -- Calculate total salary for department
    SELECT SUM(salary)
    INTO v_total_salary
    FROM plsql_dev.employees
    WHERE department = p_department_id;
    
    -- Add 20% overhead
    p_budget := v_total_salary * 1.2;
    
    DBMS_OUTPUT.PUT_LINE('Department budget: ' || p_budget);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('No employees found in department.');
        p_budget := 0;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error calculating budget: ' || SQLERRM);
        p_budget := 0;
END calculate_department_budget;
/

-- Grant execute permissions
GRANT EXECUTE ON add_employee TO plsql_dev;
GRANT EXECUTE ON update_employee_salary TO plsql_dev;
GRANT EXECUTE ON get_employee_by_department TO plsql_dev;
GRANT EXECUTE ON calculate_department_budget TO plsql_dev;