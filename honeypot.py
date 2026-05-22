import socket
import threading
import csv
import os
from datetime import datetime

os.makedirs('logs', exist_ok=True)

LOG_FILE = 'logs/honeypot_log.csv'

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'ip_address', 'port', 'status'])

def log_connection(ip, port, status):
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ip, port, status
        ])
    print(f"[HONEYPOT] Connection from {ip} on port {port} — {status}")

def handle_client(conn, addr, port):
    ip = addr[0]
    log_connection(ip, port, 'Trapped')
    try:
        conn.send(b"Welcome\n")
        conn.close()
    except:
        pass

def start_listener(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', port))
        s.listen(5)
        print(f"[HONEYPOT] Listening on port {port}")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, port)
            )
            t.daemon = True
            t.start()
    except Exception as e:
        print(f"Could not start on port {port}: {e}")

ports = [2222, 8021, 8082]
print("[HONEYPOT] Starting... Press Ctrl+C to stop")
print("[HONEYPOT] Waiting for attackers to connect...")

threads = []
for port in ports:
    t = threading.Thread(target=start_listener, args=(port,))
    t.daemon = True
    t.start()
    threads.append(t)

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n[HONEYPOT] Stopped")