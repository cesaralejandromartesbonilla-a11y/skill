#!/usr/bin/env python3
"""
Universal Asset Converter CLI
Orquestador unificado para extraer y convertir activos de motores (Unity, Unreal Engine)
a formatos finales (Godot glTF/GLB, FBX, USD) utilizando Blender 5.0 Headless.

Uso:
    python tools/asset_converter.py port --mesh <malla> --output <salida.glb> [opciones]
    python tools/asset_converter.py unity-dump <archivo.assets> --output <dir>
    python tools/asset_converter.py unity-to-glb --input <archivo.assets> --mesh-name <nombre> --output <modelo.glb>
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Ruta fija por defecto a Blender 5.0
BLENDER_DEFAULT_PATH = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
BRIDGE_SCRIPT = Path(__file__).parent / "blender_universal_bridge.py"
UNITY_EXTRACTOR = Path(__file__).parent / "unity_asset_extractor.py"

def run_blender_bridge(blender_path: str, bridge_args: list):
    """Invoca Blender 5.0 en modo headless pasando los argumentos al script puente."""
    if not os.path.exists(blender_path):
        print(f"[!] Error: No se encontró Blender en: {blender_path}")
        sys.exit(1)
        
    cmd = [blender_path, "-b", "--python", str(BRIDGE_SCRIPT.resolve()), "--"] + bridge_args
    print(f"[*] Ejecutando Blender 5.0 Headless...")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[!] Blender terminó con código de error: {result.returncode}")
        sys.exit(result.returncode)

def handle_port(args, blender_path):
    bridge_args = ["--mesh", args.mesh, "--output", args.output]
    if args.name: bridge_args += ["--name", args.name]
    if args.anims: bridge_args += ["--anims"] + args.anims
    if args.albedo: bridge_args += ["--albedo", args.albedo]
    if args.normal: bridge_args += ["--normal", args.normal]
    if args.roughness: bridge_args += ["--roughness", args.roughness]
    if args.metallic: bridge_args += ["--metallic", args.metallic]
    if args.invert_normal_y: bridge_args += ["--invert-normal-y"]
    if args.clean_vertex_colors: bridge_args += ["--clean-vertex-colors"]
    if args.two_sided: bridge_args += ["--two-sided"]
    if args.alpha_scissor is not None: bridge_args += ["--alpha-scissor", str(args.alpha_scissor)]
    if args.format: bridge_args += ["--format", args.format]
    
    run_blender_bridge(blender_path, bridge_args)

def handle_unity_dump(args):
    cmd = [sys.executable, str(UNITY_EXTRACTOR.resolve()), "extract", args.input, "--output", args.output]
    if args.types: cmd += ["--types"] + args.types
    if args.filter: cmd += ["--filter", args.filter]
    subprocess.run(cmd, check=True)

def handle_unity_to_glb(args, blender_path):
    """Extrae un modelo de Unity y lo pasa directamente a GLB en un solo paso."""
    temp_dir = Path("tmp_unity_extract")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Paso 1: Extrayendo malla '{args.mesh_name}' desde {args.input}...")
    cmd_extract = [
        sys.executable, str(UNITY_EXTRACTOR.resolve()), "extract", args.input,
        "--output", str(temp_dir),
        "--types", "Mesh", "Texture2D",
        "--filter", args.mesh_name
    ]
    subprocess.run(cmd_extract, check=True)
    
    mesh_file = temp_dir / "Mesh" / f"{args.mesh_name}.obj"
    if not mesh_file.exists():
        candidates = list((temp_dir / "Mesh").glob("*.obj"))
        if candidates:
            mesh_file = candidates[0]
        else:
            print(f"[!] Error: No se encontró la malla generada para '{args.mesh_name}'.")
            return
            
    print(f"[*] Paso 2: Procesando en Blender 5.0 y exportando a GLB...")
    bridge_args = [
        "--mesh", str(mesh_file),
        "--output", args.output
    ]
    if args.albedo: bridge_args += ["--albedo", args.albedo]
    if args.normal: bridge_args += ["--normal", args.normal]
    if args.two_sided: bridge_args += ["--two-sided"]
    
    run_blender_bridge(blender_path, bridge_args)
    print(f"[✓] Proceso completado: {args.output}")

def main():
    parser = argparse.ArgumentParser(description="Universal Asset Converter (Unity/Unreal to Blender 5.0/Godot)")
    parser.add_argument("--blender-path", default=BLENDER_DEFAULT_PATH, help="Ruta al ejecutable de Blender")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    
    # Subcomando port
    port_parser = subparsers.add_parser("port", help="Procesa y exporta una malla mediante Blender 5.0")
    port_parser.add_argument("--mesh", required=True, help="Archivo .obj, .fbx, .psk, .uemodel")
    port_parser.add_argument("--output", required=True, help="Destino (.glb, .fbx, .usd)")
    port_parser.add_argument("--name", help="Nombre del modelo")
    port_parser.add_argument("--anims", nargs="+", help="Archivos de animación (.psa, etc.)")
    port_parser.add_argument("--albedo", help="Textura Albedo")
    port_parser.add_argument("--normal", help="Textura Normal Map")
    port_parser.add_argument("--roughness", help="Textura Rugosidad")
    port_parser.add_argument("--metallic", help="Textura Metálico")
    port_parser.add_argument("--invert-normal-y", action="store_true", help="Invertir normal DirectX a OpenGL")
    port_parser.add_argument("--clean-vertex-colors", action="store_true", help="Limpiar colores de vértices")
    port_parser.add_argument("--two-sided", action="store_true", help="Material de doble cara (follaje)")
    port_parser.add_argument("--alpha-scissor", type=float, default=None, help="Recorte alfa")
    port_parser.add_argument("--format", choices=["glb", "gltf", "fbx", "usd"], help="Formato final")
    
    # Subcomando unity-dump
    dump_parser = subparsers.add_parser("unity-dump", help="Extrae activos de Unity a disco")
    dump_parser.add_argument("input", help="Archivo .assets, .bundle o carpeta")
    dump_parser.add_argument("--output", "-o", default="extracted_unity", help="Directorio de salida")
    dump_parser.add_argument("--types", "-t", nargs="+", help="Tipos a extraer (Mesh, Texture2D, etc.)")
    dump_parser.add_argument("--filter", "-f", help="Filtro de nombre")
    
    # Subcomando unity-to-glb
    u2g_parser = subparsers.add_parser("unity-to-glb", help="Extrae de Unity y convierte a GLB en un solo paso")
    u2g_parser.add_argument("--input", required=True, help="Archivo .assets o .bundle de Unity")
    u2g_parser.add_argument("--mesh-name", required=True, help="Nombre de la malla a extraer")
    u2g_parser.add_argument("--output", required=True, help="Archivo .glb de salida")
    u2g_parser.add_argument("--albedo", help="Ruta a textura albedo")
    u2g_parser.add_argument("--normal", help="Ruta a textura normal")
    u2g_parser.add_argument("--two-sided", action="store_true", help="Material doble cara")
    
    args = parser.parse_args()
    
    if args.subcommand == "port":
        handle_port(args, args.blender_path)
    elif args.subcommand == "unity-dump":
        handle_unity_dump(args)
    elif args.subcommand == "unity-to-glb":
        handle_unity_to_glb(args, args.blender_path)

if __name__ == "__main__":
    main()
