#!/usr/bin/env python3
"""
MCP Catalog Manager & Config Exporter
Administra el catálogo de servidores MCP (mcp/catalog.json) y genera
configuraciones para Antigravity (~/.gemini/config/mcp_config.json), Claude Desktop o Cursor.

Uso:
    python tools/mcp_manager.py list
    python tools/mcp_manager.py show <server-id>
    python tools/mcp_manager.py export [--target antigravity|claude] [--out-file ruta]
    python tools/mcp_manager.py new-audit <server-id>
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Configurar salida UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

CATALOG_PATH = Path("mcp/catalog.json")
AUDIT_TEMPLATE_PATH = Path("mcp/templates/MCP_AUDIT.template.md")
EVALUATED_DIR = Path("mcp/evaluated")

def load_catalog():
    if not CATALOG_PATH.exists():
        print(f"[!] No se encontró el catálogo en {CATALOG_PATH}")
        sys.exit(1)
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def list_servers():
    catalog = load_catalog()
    servers = catalog.get("servers", [])
    print(f"[*] Catálogo de Servidores MCP ({len(servers)} registrados):\n")
    print(f"| ID | Nombre | Categoría | Estado | Seguridad | Herramientas Clave |")
    print(f"| :--- | :--- | :--- | :---: | :---: | :--- |")
    for s in servers:
        status_icon = "🟢" if s["status"] == "operational" else ("🟡" if s["status"] == "verified" else "⚪")
        tools_str = ", ".join(s.get("tools_provided", [])[:3])
        print(f"| **{s['id']}** | {s['name']} | {s['category']} | {status_icon} {s['status']} | {s.get('security_tier', 'n/a')} | {tools_str} |")

def show_server(server_id: str):
    catalog = load_catalog()
    for s in catalog.get("servers", []):
        if s["id"] == server_id:
            print(f"\n=== Servidor MCP: {s['name']} ({s['id']}) ===")
            print(f"Categoría:     {s.get('category')}")
            print(f"Estado:        {s.get('status')}")
            print(f"Repositorio:   {s.get('repository')}")
            print(f"Transporte:    {s.get('transport')}")
            print(f"Nivel Seguro:  {s.get('security_tier')}")
            print(f"Descripción:   {s.get('description')}\n")
            print("Herramientas provistas:")
            for t in s.get("tools_provided", []):
                print(f"  • {t}")
            print("\nConfiguración MCP:")
            print(json.dumps({s['id']: s.get("config", {})}, indent=2))
            return
    print(f"[!] No se encontró ningún servidor con ID '{server_id}'.")

def export_config(target: str, out_file: str = None):
    catalog = load_catalog()
    mcp_servers = {}
    for s in catalog.get("servers", []):
        if s.get("status") in ["operational", "verified"]:
            mcp_servers[s["id"]] = s.get("config", {})
            
    final_json = {"mcpServers": mcp_servers}
    formatted = json.dumps(final_json, indent=2)
    
    if out_file:
        out_p = Path(out_file)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(formatted, encoding="utf-8")
        print(f"[✓] Configuración MCP exportada para {target} en: {out_p.resolve()}")
    else:
        print(formatted)

def new_audit(server_id: str):
    catalog = load_catalog()
    target_server = None
    for s in catalog.get("servers", []):
        if s["id"] == server_id:
            target_server = s
            break
            
    if not target_server:
        print(f"[!] No se encontró el servidor '{server_id}' en el catálogo.")
        return
        
    EVALUATED_DIR.mkdir(parents=True, exist_ok=True)
    out_audit = EVALUATED_DIR / f"{server_id}.md"
    
    if out_audit.exists():
        print(f"[i] El reporte de auditoría ya existe en: {out_audit}")
        return
        
    if not AUDIT_TEMPLATE_PATH.exists():
        print("[!] Falta la plantilla de auditoría.")
        return
        
    template = AUDIT_TEMPLATE_PATH.read_text(encoding="utf-8")
    content = (
        template
        .replace("{{SERVER_NAME}}", target_server.get("name", server_id))
        .replace("{{SERVER_ID}}", server_id)
        .replace("{{DATE}}", "2026-10-26")
        .replace("{{REPOSITORY_URL}}", target_server.get("repository", ""))
        .replace("{{PACKAGE_OR_COMMAND}}", target_server.get("package", ""))
        .replace("{{CATEGORY}}", target_server.get("category", ""))
        .replace("{{PURPOSE_SUMMARY}}", target_server.get("description", ""))
    )
    
    out_audit.write_text(content, encoding="utf-8")
    print(f"[+] Plantilla de auditoría generada en: {out_audit}")

def main():
    parser = argparse.ArgumentParser(description="MCP Catalog Manager & Exporter")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # list
    subparsers.add_parser("list", help="Lista los servidores catalogados")
    
    # show
    show_parser = subparsers.add_parser("show", help="Muestra el detalle y configuración de un servidor")
    show_parser.add_argument("server_id", help="ID del servidor en el catálogo")
    
    # export
    export_parser = subparsers.add_parser("export", help="Exporta la configuración JSON consolidada")
    export_parser.add_argument("--target", default="antigravity", choices=["antigravity", "claude", "cursor"])
    export_parser.add_argument("--out-file", "-o", help="Ruta de guardado (opcional)")
    
    # new-audit
    audit_parser = subparsers.add_parser("new-audit", help="Crea un archivo de auditoría inicial para un servidor")
    audit_parser.add_argument("server_id", help="ID del servidor")
    
    args = parser.parse_args()
    
    if args.subcommand == "list":
        list_servers()
    elif args.subcommand == "show":
        show_server(args.server_id)
    elif args.subcommand == "export":
        export_config(args.target, args.out_file)
    elif args.subcommand == "new-audit":
        new_audit(args.server_id)

if __name__ == "__main__":
    main()
