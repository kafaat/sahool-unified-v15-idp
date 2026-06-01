"""
SAHOOL Kong LAN Proxy
Exposes Docker's Kong gateway (127.0.0.1:8000) on the LAN interface
so Android phones can reach it at 192.168.0.154:8000.

Run as a regular user - no admin required.
Windows Firewall may prompt on first connection - click "Allow".

Usage:
    python scripts/kong-lan-proxy.py
    python scripts/kong-lan-proxy.py --lan-ip 192.168.0.154 --port 8000
"""

import socket
import threading
import argparse
import sys
import time

BACKEND_HOST = '127.0.0.1'
BACKEND_PORT = 8000


def pipe(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(16384)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        try:
            src.close()
        except OSError:
            pass
        try:
            dst.close()
        except OSError:
            pass


def handle_client(client: socket.socket, addr: tuple) -> None:
    try:
        backend = socket.create_connection((BACKEND_HOST, BACKEND_PORT), timeout=10)
    except OSError as e:
        print(f'  ✗ Cannot reach {BACKEND_HOST}:{BACKEND_PORT} — is Kong running? ({e})')
        client.close()
        return

    t1 = threading.Thread(target=pipe, args=(client, backend), daemon=True)
    t2 = threading.Thread(target=pipe, args=(backend, client), daemon=True)
    t1.start()
    t2.start()


def main() -> None:
    parser = argparse.ArgumentParser(description='SAHOOL Kong LAN Proxy')
    parser.add_argument('--lan-ip', default='192.168.0.154',
                        help='Windows LAN IP to listen on (default: 192.168.0.154)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port to listen on (default: 8000)')
    args = parser.parse_args()

    lan_ip = args.lan_ip
    port = args.port

    # Verify backend is reachable first
    print(f'Checking Kong at {BACKEND_HOST}:{BACKEND_PORT}...', end=' ', flush=True)
    try:
        with socket.create_connection((BACKEND_HOST, BACKEND_PORT), timeout=5):
            print('OK')
    except OSError as e:
        print(f'FAILED\nERROR: Cannot reach Kong at {BACKEND_HOST}:{BACKEND_PORT}: {e}')
        print('Make sure Docker containers are running: docker compose up -d kong')
        sys.exit(1)

    # Bind to the LAN IP only (won't conflict with Docker's 127.0.0.1:8000)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((lan_ip, port))
    except OSError as e:
        print(f'ERROR: Cannot bind to {lan_ip}:{port}: {e}')
        if 'address' in str(e).lower() or '10049' in str(e):
            print(f'Is {lan_ip} your current PC LAN IP?')
            print('Run: ipconfig | findstr "IPv4"')
        elif '10048' in str(e) or 'already in use' in str(e).lower():
            print(f'Port {port} is already in use on {lan_ip}')
        sys.exit(1)

    server.listen(50)
    print(f'')
    print(f'  Kong LAN Proxy running')
    print(f'  Phone connects to:  http://{lan_ip}:{port}')
    print(f'  Forwarding to:      http://{BACKEND_HOST}:{BACKEND_PORT}')
    print(f'')
    print(f'  Leave this window open while testing the app.')
    print(f'  Windows Firewall may prompt — click "Allow".')
    print(f'  Press Ctrl+C to stop.')
    print(f'')

    try:
        while True:
            try:
                client, addr = server.accept()
                threading.Thread(
                    target=handle_client,
                    args=(client, addr),
                    daemon=True,
                ).start()
            except OSError:
                break
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.close()


if __name__ == '__main__':
    main()
