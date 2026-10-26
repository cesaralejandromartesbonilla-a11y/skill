#!/usr/bin/env python3
"""
MCP Local Sandbox Runner (powered by vercel-labs/emulate)
Inicia emuladores locales con estado para 14 servicios (GitHub, AWS, Stripe, Slack, etc.)
permitiendo probar servidores MCP y agentes sin conexión a internet ni consumo de saldo.

Uso:
    python tools/sandbox_runner.py list
    python tools/sandbox_runner.py start [--port 3000] [--services github slack]
    python tools/sandbox_runner.py check [--port 3000]
"""

import sys
import subprocess
import argparse
import urllib.request
import json
from pathlib import Path

# Configurar salida UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def list_available_services():
    print("[*] Consultando servicios disponibles en emulate...")
    try:
        subprocess.run(["npx", "-y", "emulate", "list"], check=True)
    except Exception as e:
        print(f"[!] Error ejecutando npx emulate list: {e}")

def check_sandbox(port: int):
    url = f"http://localhost:{port}/_emulate"
    print(f"[*] Comprobando estado del sandbox en {url}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Sandbox-Check/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                print(f"[✓] Sandbox local activo y respondiendo en el puerto {port}.")
                return True
    except Exception as e:
        print(f"[-] Sandbox no activo en el puerto {port} ({e}).")
        return False

def start_sandbox(port: int, services=None):
    cmd = ["npx", "-y", "emulate", "start", "--port", str(port)]
    if services:
        for s in services:
            cmd += ["--service", s]
            
    print(f"[*] Iniciando sandbox local en puerto {port}...")
    print(f"[*] Comando: {' '.join(cmd)}")
    print("[i] Presiona Ctrl+C para detener el servidor.\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[*] Sandbox detenido.")

def main():
    parser = argparse.ArgumentParser(description="MCP Sandbox Runner via emulate")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # list
    subparsers.add_parser("list", help="Lista los servicios soportados por el sandbox")
    
    # check
    check_parser = subparsers.add_parser("check", help="Comprueba si el sandbox local está corriendo")
    check_parser.add_argument("--port", "-p", type=int, default=3000, help="Puerto del sandbox")
    
    # start
    start_parser = subparsers.add_parser("start", help="Inicia el servidor sandbox en local")
    start_parser.add_argument("--port", "-p", type=int, default=3000, help="Puerto de escucha (default 3000)")
    start_parser.add_argument("--services", "-s", nargs="+", help="Servicios específicos a habilitar (ej. github slack aws)")
    
    args = parser.parse_args()
    
    if args.subcommand == "list":
        list_available_services()
    elif args.subcommand == "check":
        check_sandbox(args.port)
    elif args.subcommand == "start":
        start_sandbox(args.port, args.services)

if __name__ == "__main__":
    main()
