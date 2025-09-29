#!/usr/bin/env python3
"""
Integration tests for the Basic Port Scanner.
"""

import unittest
import subprocess
import time
import sys
import os

class TestPortScanner(unittest.TestCase):
    """Test cases for the port scanner."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.script_path = os.path.join(os.path.dirname(__file__), 'scanner.py')
    
    def test_localhost_scan(self):
        """Test scanning localhost with a known open port."""
        # Start a test server on port 8080
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8080"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1)  # Allow server to start
        
        try:
            # Run scanner
            result = subprocess.run(
                [sys.executable, self.script_path, "--host", "localhost", "--ports", "8000-8100"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check results
            self.assertEqual(result.returncode, 0)
            self.assertIn("Port 8080 is open", result.stdout)
        finally:
            # Cleanup
            server.terminate()
            server.wait()
    
    def test_invalid_host(self):
        """Test error handling for invalid hosts."""
        result = subprocess.run(
            [sys.executable, self.script_path, "--host", "invalid.domain.xyz", "--ports", "1-10"],
            capture_output=True,
            text=True
        )
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Hostname could not be resolved", result.stdout)
    
    def test_invalid_port_range(self):
        """Test error handling for invalid port ranges."""
        # Test invalid format
        result = subprocess.run(
            [sys.executable, self.script_path, "--host", "localhost", "--ports", "invalid"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid port range format", result.stdout)
        
        # Test invalid range values
        result = subprocess.run(
            [sys.executable, self.script_path, "--host", "localhost", "--ports", "100-1"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid port range", result.stdout)
        
        # Test out of range ports
        result = subprocess.run(
            [sys.executable, self.script_path, "--host", "localhost", "--ports", "0-70000"],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid port range", result.stdout)

if __name__ == "__main__":
    unittest.main()