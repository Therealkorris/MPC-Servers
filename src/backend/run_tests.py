#!/usr/bin/env python3
"""
Run tests for the Visio AI backend.
"""

import os
import sys
import argparse
import subprocess

def main():
    """Run the tests for the backend."""
    parser = argparse.ArgumentParser(description="Run tests for the Visio AI backend")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--test-path", "-p", default="tests", help="Path to the tests directory")
    parser.add_argument("--specific-test", "-t", help="Run a specific test file or function")
    args = parser.parse_args()
    
    # Build the pytest command
    cmd = ["pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.specific_test:
        cmd.append(args.specific_test)
    else:
        cmd.append(args.test_path)
    
    # Run the tests
    print(f"Running tests with command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 