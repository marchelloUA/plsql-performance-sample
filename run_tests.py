#!/usr/bin/env python3
"""
Test runner script for the PL/SQL Performance Sample project
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_pytest_tests(test_type="all", verbose=True, coverage=False):
    """Run pytest tests with specified options"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Change to project root
    os.chdir(project_root)
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add options based on arguments
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=python", "--cov-report=html", "--cov-report=term"])
    
    # Add test type filter
    if test_type == "unit":
        cmd.extend(["tests/unit"])
    elif test_type == "integration":
        cmd.extend(["tests/integration"])
    elif test_type == "all":
        cmd.extend(["tests"])
    else:
        print(f"Unknown test type: {test_type}")
        return 1
    
    # Add markers for integration tests
    if test_type in ["integration", "all"]:
        cmd.extend(["-m", "integration"])
    
    # Run the tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def run_specific_test_file(test_file):
    """Run a specific test file"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Change to project root
    os.chdir(project_root)
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    
    # Run the tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for PL/SQL Performance Sample project")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate test coverage report"
    )
    parser.add_argument(
        "--file", 
        help="Run a specific test file"
    )
    
    args = parser.parse_args()
    
    if args.file:
        # Run specific test file
        return run_specific_test_file(args.file)
    else:
        # Run tests based on type
        return run_pytest_tests(args.type, args.verbose, args.coverage)

if __name__ == "__main__":
    sys.exit(main())