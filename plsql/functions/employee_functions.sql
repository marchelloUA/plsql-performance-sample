-- Employee Management Functions
-- This file contains functions for employee data operations

CREATE OR REPLACE FUNCTION get_employee_count(
    p_department_id IN NUMBER DEFAULT NULL
) RETURN NUMBER
IS
    v_count NUMBER;
BEGIN
    IF p_department_id IS NULL THEN
        -- Get total employee count
        SELECT COUNT(*)
        INTO v_count
        FROM plsql_dev.employees;
    ELSE
        -- Get count for specific department
        SELECT COUNT(*)
        INTO v_count
        FROM plsql_dev.employees
        WHERE department = p_department_id;
    END IF;
    
    RETURN v_count;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0;
END get_employee_count;
/

CREATE OR REPLACE FUNCTION get_average_salary(
    p_department_id IN NUMBER DEFAULT NULL
) RETURN NUMBER
IS
    v_avg_salary NUMBER;
BEGIN
    IF p_department_id IS NULL THEN
        -- Get average salary across all departments
        SELECT AVG(salary)
        INTO v_avg_salary
        FROM plsql_dev.employees;
    ELSE
        -- Get average salary for specific department
        SELECT AVG(salary)
        INTO v_avg_salary
        FROM plsql_dev.employees
        WHERE department = p_department_id;
    END IF;
    
    RETURN NVL(v_avg_salary, 0);
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0;
END get_average_salary;
/

CREATE OR REPLACE FUNCTION get_employee_tenure(
    p_employee_id IN NUMBER
) RETURN NUMBER
IS
    v_hire_date DATE;
    v_tenure NUMBER;
BEGIN
    -- Get hire date
    SELECT hire_date
    INTO v_hire_date
    FROM plsql_dev.employees
    WHERE employee_id = p_employee_id;
    
    -- Calculate tenure in years
    v_tenure := MONTHS_BETWEEN(SYSDATE, v_hire_date) / 12;
    
    RETURN v_tenure;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
    WHEN OTHERS THEN
        RETURN 0;
END get_employee_tenure;
/

CREATE OR REPLACE FUNCTION is_eligible_for_bonus(
    p_employee_id IN NUMBER
) RETURN VARCHAR2
IS
    v_salary NUMBER;
    v_tenure NUMBER;
    v_department VARCHAR2(50);
BEGIN
    -- Get employee details
    SELECT salary, department
    INTO v_salary, v_department
    FROM plsql_dev.employees
    WHERE employee_id = p_employee_id;
    
    -- Get tenure
    v_tenure := get_employee_tenure(p_employee_id);
    
    -- Determine eligibility
    IF v_salary > 80000 AND v_tenure > 2 THEN
        RETURN 'Eligible';
    ELSIF v_department = 'IT' AND v_salary > 70000 THEN
        RETURN 'Eligible';
    ELSE
        RETURN 'Not Eligible';
    END IF;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 'Employee Not Found';
    WHEN OTHERS THEN
        RETURN 'Error';
END is_eligible_for_bonus;
/

CREATE OR REPLACE FUNCTION get_highest_paid_employee(
    p_department_id IN NUMBER DEFAULT NULL
) RETURN VARCHAR2
IS
    v_employee_name VARCHAR2(100);
    v_max_salary NUMBER;
BEGIN
    IF p_department_id IS NULL THEN
        -- Get highest paid employee overall
        SELECT employee_name
        INTO v_employee_name
        FROM (
            SELECT employee_name
            FROM plsql_dev.employees
            ORDER BY salary DESC
            FETCH FIRST 1 ROWS ONLY
        );
    ELSE
        -- Get highest paid employee in department
        SELECT employee_name
        INTO v_employee_name
        FROM (
            SELECT employee_name
            FROM plsql_dev.employees
            WHERE department = p_department_id
            ORDER BY salary DESC
            FETCH FIRST 1 ROWS ONLY
        );
    END IF;
    
    RETURN v_employee_name;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 'No employees found';
    WHEN OTHERS THEN
        RETURN 'Error';
END get_highest_paid_employee;
/

-- Grant execute permissions
GRANT EXECUTE ON get_employee_count TO plsql_dev;
GRANT EXECUTE ON get_average_salary TO plsql_dev;
GRANT EXECUTE ON get_employee_tenure TO plsql_dev;
GRANT EXECUTE ON is_eligible_for_bonus TO plsql_dev;
GRANT EXECUTE ON get_highest_paid_employee TO plsql_dev;