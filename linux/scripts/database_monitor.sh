#!/bin/bash

# Database Monitoring Script
# Monitors database containers and system resources

# Configuration
ORACLE_CONTAINER="oracle-free"
SQLSERVER_CONTAINER="sql-server"
LOG_FILE="/var/log/database_monitor.log"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=85

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_message "ERROR: Docker is not running"
        exit 1
    fi
}

# Check container status
check_container_status() {
    local container_name=$1
    local status=$(docker ps --filter "name=$container_name" --format "{{.Status}}")
    
    if [[ $status == *"Up"* ]]; then
        log_message "Container $container_name is running: $status"
        return 0
    else
        log_message "WARNING: Container $container_name is not running properly: $status"
        return 1
    fi
}

# Check database connectivity
check_database_connectivity() {
    local db_type=$1
    
    case $db_type in
        "oracle")
            # Check Oracle connectivity
            if docker exec $ORACLE_CONTAINER sqlplus -s sys/YourPassword123@localhost:1521/FREEPDB1 as sysdba @/tmp/oracle_test.sql >/dev/null 2>&1; then
                log_message "Oracle database connectivity: OK"
                return 0
            else
                log_message "ERROR: Oracle database connectivity failed"
                return 1
            fi
            ;;
        "sqlserver")
            # Check SQL Server connectivity
            if docker exec $SQLSERVER_CONTAINER /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword123!' -Q "SELECT 1" >/dev/null 2>&1; then
                log_message "SQL Server database connectivity: OK"
                return 0
            else
                log_message "ERROR: SQL Server database connectivity failed"
                return 1
            fi
            ;;
        *)
            log_message "ERROR: Unknown database type: $db_type"
            return 1
            ;;
    esac
}

# Check system resources
check_system_resources() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    local memory_usage=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    log_message "System Resources - CPU: ${cpu_usage}%, Memory: ${memory_usage}%, Disk: ${disk_usage}%"
    
    # Check for alerts
    if (( $(echo "$cpu_usage > $ALERT_THRESHOLD_CPU" | bc -l) )); then
        log_message "ALERT: CPU usage is ${cpu_usage}% (threshold: ${ALERT_THRESHOLD_CPU}%)"
    fi
    
    if (( $(echo "$memory_usage > $ALERT_THRESHOLD_MEMORY" | bc -l) )); then
        log_message "ALERT: Memory usage is ${memory_usage}% (threshold: ${ALERT_THRESHOLD_MEMORY}%)"
    fi
    
    if [ "$disk_usage" -gt 90 ]; then
        log_message "ALERT: Disk usage is ${disk_usage}% (threshold: 90%)"
    fi
}

# Check container resources
check_container_resources() {
    local container_name=$1
    
    log_message "Checking resources for container: $container_name"
    
    # Get container stats
    local stats=$(docker stats $container_name --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}")
    log_message "Container $container_name stats:"
    log_message "$stats"
}

# Main monitoring function
main() {
    log_message "Starting database monitoring"
    
    # Check Docker
    check_docker
    
    # Check container status
    check_container_status $ORACLE_CONTAINER
    ORACLE_STATUS=$?
    
    check_container_status $SQLSERVER_CONTAINER
    SQLSERVER_STATUS=$?
    
    # Check database connectivity
    if [ $ORACLE_STATUS -eq 0 ]; then
        check_database_connectivity "oracle"
    fi
    
    if [ $SQLSERVER_STATUS -eq 0 ]; then
        check_database_connectivity "sqlserver"
    fi
    
    # Check system resources
    check_system_resources
    
    # Check container resources
    if [ $ORACLE_STATUS -eq 0 ]; then
        check_container_resources $ORACLE_CONTAINER
    fi
    
    if [ $SQLSERVER_STATUS -eq 0 ]; then
        check_container_resources $SQLSERVER_CONTAINER
    fi
    
    log_message "Database monitoring completed"
}

# Create temporary SQL test file
create_test_files() {
    cat > /tmp/oracle_test.sql << EOF
SET HEADING OFF
SET PAGESIZE 0
SELECT 'OK' FROM DUAL;
EXIT;
EOF
}

# Cleanup function
cleanup() {
    rm -f /tmp/oracle_test.sql
    log_message "Monitoring script completed"
}

# Signal handler
trap cleanup EXIT

# Create test files
create_test_files

# Run main function
main "$@"