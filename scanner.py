#!/usr/bin/env python3
"""
Basic TCP Port Scanner
A concurrent port scanner that identifies open TCP ports on a target host.
"""

import socket
import sys
import argparse
import threading
from queue import Queue

# Constants
DEFAULT_TIMEOUT = 1.0
MAX_THREADS = 100

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Basic TCP Port Scanner",
        epilog="Example: python scanner.py --host example.com --ports 1-1024"
    )
    parser.add_argument("--host", required=True, help="Target host (IP or domain)")
    parser.add_argument("--ports", required=True, help="Port range (e.g. 20-80)")
    return parser.parse_args()

def scan_port(host, port, timeout=DEFAULT_TIMEOUT):
    """
    Attempt to connect to a TCP port and return port if open.
    
    Args:
        host (str): Target host
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds
        
    Returns:
        int: Port number if open, None otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            return port if result == 0 else None
    except socket.gaierror:
        print("Hostname could not be resolved")
        sys.exit(1)
    except socket.error:
        print("Couldn't connect to server")
        sys.exit(1)
    except Exception as e:
        print(f"Error scanning port {port}: {str(e)}")
        return None

def threader(host, port_queue, open_ports):
    """Worker thread function to process ports from the queue."""
    while not port_queue.empty():
        port = port_queue.get()
        result = scan_port(host, port)
        if result:
            open_ports.append(result)
        port_queue.task_done()

def main():
    """Main function to execute the port scanner."""
    args = parse_args()
    
    try:
        start_port, end_port = map(int, args.ports.split('-'))
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError("Invalid port range")
    except ValueError:
        print("Invalid port range format. Use: start-end (e.g. 20-80)")
        sys.exit(1)
    
    print(f"Starting scan on host {args.host}")
    
    port_queue = Queue()
    open_ports = []
    
    # Populate queue with ports to scan
    for port in range(start_port, end_port + 1):
        port_queue.put(port)
    
    # Start threads
    for _ in range(MAX_THREADS):
        t = threading.Thread(
            target=threader,
            args=(args.host, port_queue, open_ports)
        )
        t.daemon = True
        t.start()
    
    # Wait for all threads to complete
    port_queue.join()
    
    # Display results
    if open_ports:
        print("\nOpen ports:")
        for port in sorted(open_ports):
            print(f"Port {port} is open")
    else:
        print("\nNo open ports found")

if __name__ == "__main__":
    main()