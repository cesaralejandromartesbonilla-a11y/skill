"""
Ecosystem Discovery Tool: Skills & MCP Servers
Permite buscar habilidades (skills) y servidores MCP en la comunidad.
Uso:
    python tools/search_ecosystem.py skills <query>
    python tools/search_ecosystem.py mcp <query>
    python tools/search_ecosystem.py trending-mcp
"""

import sys
import subprocess
import json
import urllib.request
import urllib.parse
import io

# Asegurar codificación UTF-8 en salida estándar de Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def run_skills_find(query: str):
    """Invoca el CLI de vercel-labs/skills para buscar skills."""
    print(f"[*] Buscando skills para: '{query}'...")
    try:
        result = subprocess.run(
            ["npx", "-y", "skills", "find", query],
            capture_output=True,
            text=True,
            check=False
        )
        print(result.stdout or result.stderr)
    except Exception as e:
        print(f"[!] Error ejecutando npx skills find: {e}")

def search_github_mcp(query: str, max_results: int = 8):
    """Busca repositorios de servidores MCP en GitHub."""
    search_term = f"{query} topic:mcp-server OR modelcontextprotocol"
    encoded_query = urllib.parse.quote(search_term)
    url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page={max_results}"

    print(f"[*] Buscando servidores MCP en GitHub: '{query}'...")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Skill-Hub-Discovery/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                items = data.get("items", [])
                if not items:
                    print("[-] No se encontraron repositorios MCP coincidentes.")
                    return

                print(f"[+] Se encontraron {len(items)} repositorios relevantes:\n")
                print(f"| Repositorio | Stars | Descripción | URL |")
                print(f"| :--- | :---: | :--- | :--- |")
                for item in items:
                    repo_name = item.get("full_name")
                    stars = item.get("stargazers_count", 0)
                    desc = (item.get("description") or "Sin descripción").replace("\n", " ")[:80]
                    html_url = item.get("html_url")
                    print(f"| **{repo_name}** | ⭐ {stars} | {desc} | [Link]({html_url}) |")
            else:
                print(f"[!] Error HTTP {response.status}")
    except Exception as e:
        print(f"[!] Error consultando la API de GitHub: {e}")

def get_trending_mcp():
    """Obtiene los repositorios de MCP más populares actualmente."""
    search_github_mcp("mcp", max_results=10)

def main():
    if len(sys.argv) < 2:
        print("Uso: python tools/search_ecosystem.py [skills|mcp|trending-mcp] [término_de_búsqueda]")
        return

    mode = sys.argv[1].lower()
    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    if mode == "skills":
        if not query:
            print("[!] Debes proporcionar un término de búsqueda para skills.")
            return
        run_skills_find(query)
    elif mode == "mcp":
        if not query:
            query = "server"
        search_github_mcp(query)
    elif mode == "trending-mcp":
        get_trending_mcp()
    else:
        print(f"[!] Modo desconocido: {mode}. Usa 'skills', 'mcp' o 'trending-mcp'.")

if __name__ == "__main__":
    main()
