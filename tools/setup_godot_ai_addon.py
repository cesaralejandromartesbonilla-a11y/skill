#!/usr/bin/env python3
"""
tools/setup_godot_ai_addon.py
=============================
Aprovisionador e instalador automatizado del addon 'godot_ai' para proyectos de Godot 4.x.

Resuelve el problema recurrente en el que los agentes evitan usar el servidor MCP
'godot-ai' por no tener instalado y configurado el plugin en el proyecto objetivo.

Operaciones en Un Solo Disparo:
1. Copia el addon completo 'godot_ai' a '<project>/addons/godot_ai/'.
2. Registra y habilita el plugin en 'project.godot' ([editor_plugins] enabled=...).
3. Registra el helper de runtime en 'project.godot' ([autoload] _mcp_game_helper=...).
4. Valida la integridad de la configuración para conexión inmediata con 'godot-ai attach'.

Uso:
    python tools/setup_godot_ai_addon.py --project <ruta_al_proyecto>
    python tools/setup_godot_ai_addon.py --project <ruta_al_proyecto> --check
    python tools/setup_godot_ai_addon.py --project <ruta_al_proyecto> --force
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


PLUGIN_RES_PATH = "res://addons/godot_ai/plugin.cfg"
AUTOLOAD_ENTRY = '_mcp_game_helper="*res://addons/godot_ai/runtime/game_helper.gd"'


def find_source_template() -> Path:
    """Busca la plantilla del addon en orden de prioridad."""
    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parent

    candidates = [
        workspace_root / "templates" / "addons" / "godot_ai",
        workspace_root / "research" / "godot-ai" / "plugin" / "addons" / "godot_ai",
        Path(r"C:\Users\cesar\Desktop\games\demos - copia\GodotProjects\01_Prototypes\proyecto-derivados\RFS22\addons\godot_ai"),
    ]

    for candidate in candidates:
        if candidate.exists() and (candidate / "plugin.cfg").exists():
            return candidate

    raise FileNotFoundError(
        "No se encontró ninguna plantilla válida de 'addons/godot_ai'. Verifique templates/addons/godot_ai."
    )


def patch_project_godot(project_godot_path: Path) -> dict:
    """
    Inspecciona y actualiza project.godot garantizando que godot_ai esté en
    [editor_plugins] y que el autoload _mcp_game_helper esté registrado.
    """
    if not project_godot_path.exists():
        raise FileNotFoundError(f"No existe el archivo {project_godot_path}")

    content = project_godot_path.read_text(encoding="utf-8")
    changes = []

    # 1. Gestionar [editor_plugins]
    if "[editor_plugins]" not in content:
        # Añadir sección [editor_plugins] al final
        content = content.rstrip() + f'\n\n[editor_plugins]\n\nenabled=PackedStringArray("{PLUGIN_RES_PATH}")\n'
        changes.append("Añadida sección [editor_plugins] con godot_ai habilitado")
    else:
        # La sección ya existe, verificar si contiene godot_ai
        editor_plugin_regex = re.compile(
            r"(\[editor_plugins\][\s\S]*?enabled=(?:PackedStringArray|\[))([\s\S]*?)(\)|\])",
            re.MULTILINE
        )
        match = editor_plugin_regex.search(content)
        if match:
            prefix, current_plugins, suffix = match.groups()
            if PLUGIN_RES_PATH not in current_plugins:
                # Extraer plugins existentes
                items = [item.strip() for item in current_plugins.split(",") if item.strip()]
                items.append(f'"{PLUGIN_RES_PATH}"')
                new_list = ", ".join(items)
                new_block = f"{prefix}{new_list}{suffix}"
                content = content[:match.start()] + new_block + content[match.end():]
                changes.append(f"Añadido {PLUGIN_RES_PATH} a enabled existente")
        else:
            # Sección existe pero sin enabled, agregar enabled
            content = content.replace("[editor_plugins]", f'[editor_plugins]\n\nenabled=PackedStringArray("{PLUGIN_RES_PATH}")')
            changes.append("Añadido campo enabled a [editor_plugins]")

    # 2. Gestionar [autoload]
    if "[autoload]" not in content:
        content = content.rstrip() + f'\n\n[autoload]\n\n{AUTOLOAD_ENTRY}\n'
        changes.append("Añadida sección [autoload] con _mcp_game_helper")
    else:
        if "_mcp_game_helper" not in content:
            autoload_regex = re.compile(r"(\[autoload\]\s*)", re.MULTILINE)
            content = autoload_regex.sub(rf"\1{AUTOLOAD_ENTRY}\n", content, count=1)
            changes.append("Añadido _mcp_game_helper a sección [autoload]")

    # Escribir de vuelta si hubo cambios
    if changes:
        project_godot_path.write_text(content, encoding="utf-8")

    return {"patched": bool(changes), "changes": changes}


def check_project_status(project_path: Path) -> dict:
    """Verifica el estado actual del proyecto sin modificarlo."""
    project_godot = project_path / "project.godot"
    addon_dir = project_path / "addons" / "godot_ai"
    plugin_cfg = addon_dir / "plugin.cfg"

    has_project_godot = project_godot.exists()
    has_addon = plugin_cfg.exists()

    plugin_enabled = False
    autoload_enabled = False

    if has_project_godot:
        content = project_godot.read_text(encoding="utf-8", errors="ignore")
        plugin_enabled = PLUGIN_RES_PATH in content
        autoload_enabled = "_mcp_game_helper" in content

    is_ready = has_project_godot and has_addon and plugin_enabled and autoload_enabled

    return {
        "project_path": str(project_path),
        "has_project_godot": has_project_godot,
        "has_addon_files": has_addon,
        "plugin_enabled": plugin_enabled,
        "autoload_registered": autoload_enabled,
        "is_ready_for_mcp": is_ready,
    }


def setup_godot_ai(project_path: Path, force: bool = False) -> dict:
    """Instala y configura el addon godot_ai en el proyecto indicado."""
    project_godot = project_path / "project.godot"
    if not project_godot.exists():
        raise FileNotFoundError(
            f"El directorio '{project_path}' no contiene 'project.godot'. Debe ser la raíz de un proyecto Godot."
        )

    target_addons_dir = project_path / "addons"
    target_godot_ai = target_addons_dir / "godot_ai"

    source_template = find_source_template()
    copied = False

    if not target_godot_ai.exists() or force:
        target_addons_dir.mkdir(parents=True, exist_ok=True)
        if target_godot_ai.exists() and force:
            shutil.rmtree(target_godot_ai)
        shutil.copytree(source_template, target_godot_ai)
        copied = True

    patch_result = patch_project_godot(project_godot)
    final_status = check_project_status(project_path)

    return {
        "status": "success",
        "project": str(project_path),
        "source_template": str(source_template),
        "addon_copied": copied,
        "patch_result": patch_result,
        "ready": final_status["is_ready_for_mcp"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Aprovisiona y configura el addon 'godot_ai' en cualquier proyecto Godot 4.x"
    )
    parser.add_argument(
        "--project", "-p",
        type=str,
        default=".",
        help="Ruta al proyecto Godot (donde reside project.godot). Por defecto: directorio actual."
    )
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="Solo comprueba el estado de configuración sin modificar ningún archivo."
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Fuerza la sobreescritura de addons/godot_ai si ya existe."
    )

    args = parser.parse_args()
    project_dir = Path(args.project).resolve()

    if args.check:
        status = check_project_status(project_dir)
        print("=== ESTADO DEL ADDON GODOT_AI ===")
        print(f"Proyecto:              {status['project_path']}")
        print(f"project.godot:         {'OK' if status['has_project_godot'] else 'FALTANTE'}")
        print(f"Archivos del Addon:    {'INSTALADOS' if status['has_addon_files'] else 'NO INSTALADOS'}")
        print(f"Plugin Habilitado:     {'SI' if status['plugin_enabled'] else 'NO'}")
        print(f"Autoload Registrado:   {'SI' if status['autoload_registered'] else 'NO'}")
        print(f"Listo para Godot-AI:   {'LISTO' if status['is_ready_for_mcp'] else 'INCOMPLETO'}")
        sys.exit(0 if status["is_ready_for_mcp"] else 1)

    try:
        result = setup_godot_ai(project_dir, force=args.force)
        print("=== APROVISIONAMIENTO DE GODOT_AI COMPLETADO ===")
        print(f"Proyecto:         {result['project']}")
        print(f"Plantilla origen: {result['source_template']}")
        print(f"Addon copiado:    {'SI' if result['addon_copied'] else 'YA EXISTÍA (omitido copy)'}")
        if result['patch_result']['changes']:
            print("Cambios en project.godot:")
            for change in result['patch_result']['changes']:
                print(f"  - {change}")
        else:
            print("project.godot:    Ya estaba correctamente configurado.")
        print(f"Conexión MCP:     {'LISTA PARA USAR' if result['ready'] else 'REVISIÓN REQUERIDA'}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
