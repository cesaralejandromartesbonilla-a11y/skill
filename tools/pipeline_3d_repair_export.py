#!/usr/bin/env python3
"""
Pipeline Universal 3D Auto-Repair & Godot Ingest
================================================
Orquestador macro de un solo disparo para agentes y desarrolladores.
Automatiza en un solo comando determinista:
1. Reparación completa de malla 3D en Blender 5.0 Headless:
   - Reset y lectura de malla (.fbx, .obj, .gltf, .glb, .psk, .blend, etc.)
   - Aplicación de transformaciones (Ctrl+A -> Rotación, Escala, Posición)
   - Normalización de pivote a la base inferior (Z=min(Z) en Blender -> Y=0 en Godot)
   - Desinfección de geometría (merge de vértices dobles a 0.1mm, normales hacia el exterior)
   - Limpieza de vertex colors si se solicita
   - Configuración PBR Principled BSDF (Albedo, Normal con inversión DirectX/OpenGL, Rugosidad, Metálico u ORM)
   - Exportación limpia y optimizada a formato .glb
2. Traslado e ingesta directa en el proyecto Godot objetivo (res://assets/<categoría>/)
3. Forzado de reimportación y registro de UID en Godot 4 (vía Godot headless)

Uso por el Agente:
    python tools/pipeline_3d_repair_export.py --input "ruta/modelo.fbx" --project "C:/ruta/ProyectoGodot" --category props
"""

import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path

# Ajustar salida utf-8 para Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BLENDER_DEFAULT_PATH = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
GODOT_DEFAULT_PATH = r"C:\Users\cesar\Downloads\Godot_v4.6.2-stable_mono_win64\Godot_v4.6.2-stable_mono_win64\Godot_v4.6.2-stable_mono_win64_console.exe"
BRIDGE_SCRIPT = Path(__file__).parent / "blender_universal_bridge.py"

def run_blender_process(blender_path: str, bridge_args: list):
    """Ejecuta Blender 5.0 headless con el puente universal."""
    if not os.path.exists(blender_path):
        raise FileNotFoundError(f"Blender ejecutable no encontrado en: {blender_path}")
        
    cmd = [blender_path, "-b", "--python", str(BRIDGE_SCRIPT.resolve()), "--"] + bridge_args
    print(f"[*] [1/3] Ejecutando reparación y exportación en Blender 5.0 Headless...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    if result.returncode != 0:
        print("[!] Error en Blender stdout:")
        print(result.stdout)
        print("[!] Error en Blender stderr:")
        print(result.stderr)
        raise RuntimeError(f"Blender falló con código de salida {result.returncode}")
        
    print("[✓] Proceso de Blender completado con éxito.")
    # Extraer mensajes clave de salida
    for line in result.stdout.splitlines():
        if line.startswith(("[+]", "[*]", "[✓]")):
            print(f"    {line}")

def ingest_to_godot(glb_temp: Path, project_dir: Path, category: str, texture_paths: list = None) -> Path:
    """Mueve el GLB exportado y sus texturas asociadas a la estructura de assets del proyecto Godot."""
    target_assets_dir = project_dir / "assets" / category
    target_assets_dir.mkdir(parents=True, exist_ok=True)
    
    target_glb = target_assets_dir / glb_temp.name
    print(f"[*] [2/3] Moviendo modelo GLB a Godot: {target_glb}")
    shutil.copy2(str(glb_temp), str(target_glb))
    
    # Copiar texturas si se especificaron
    if texture_paths:
        tex_dir = target_assets_dir / "textures"
        tex_dir.mkdir(parents=True, exist_ok=True)
        for tex in texture_paths:
            if tex and os.path.exists(tex):
                tex_p = Path(tex)
                dest_tex = tex_dir / tex_p.name
                shutil.copy2(str(tex_p), str(dest_tex))
                print(f"    [+] Textura copiada: {dest_tex.name} -> {tex_dir}")
                
    return target_glb

def trigger_godot_reimport(godot_path: str, project_dir: Path):
    """Ejecuta Godot en modo headless para escanear y generar .uid y .import automáticamente."""
    if not os.path.exists(godot_path):
        print(f"[!] Godot no encontrado en: {godot_path}. Omisión de auto-import.")
        return
        
    print(f"[*] [3/3] Forzando reimportación y generación de UID en Godot 4 headless...")
    cmd = [
        godot_path,
        "--headless",
        "--editor",
        "--quit",
        "--path", str(project_dir.resolve())
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
        print("[✓] Godot ha procesado la reimportación de assets y generado metadatos .import.")
    except subprocess.TimeoutExpired:
        print("[!] Advertencia: Tiempo de espera agotado en escaneo headless de Godot.")
    except Exception as e:
        print(f"[!] Advertencia al ejecutar Godot headless: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Universal de Reparación 3D e Ingesta a Godot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--input", required=True, help="Ruta del archivo de malla de origen (.fbx, .obj, .gltf, .psk, .blend)")
    parser.add_argument("--output", help="Ruta de salida del GLB temporal o final")
    parser.add_argument("--project", help="Ruta del proyecto Godot (res://) para ingesta automática")
    parser.add_argument("--category", default="props", help="Subcarpeta en res://assets/<categoría>/ (ej. props, characters, env)")
    parser.add_argument("--no-normalize-pivot", action="store_true", help="Desactiva la normalización del pivote a la base inferior")
    parser.add_argument("--no-apply-transforms", action="store_true", help="Desactiva la aplicación automática de transformaciones (Ctrl+A)")
    parser.add_argument("--no-sanitize", action="store_true", help="Desactiva la desinfección de geometría y cálculo de normales")
    parser.add_argument("--clean-vertex-colors", action="store_true", help="Elimina capas de colores de vértices corruptas")
    parser.add_argument("--albedo", help="Textura Albedo/BaseColor")
    parser.add_argument("--normal", help="Textura Normal Map")
    parser.add_argument("--roughness", help="Textura Roughness")
    parser.add_argument("--metallic", help="Textura Metallic")
    parser.add_argument("--orm", help="Textura ORM (R=AO, G=Roughness, B=Metallic)")
    parser.add_argument("--invert-normal-y", action="store_true", help="Invierte el canal verde del Normal Map (DirectX a OpenGL)")
    parser.add_argument("--two-sided", action="store_true", help="Doble cara para follaje o vegetación")
    parser.add_argument("--alpha-scissor", type=float, help="Umbral de Alpha Scissor")
    parser.add_argument("--blender-path", default=BLENDER_DEFAULT_PATH, help="Ruta al ejecutable de Blender")
    parser.add_argument("--godot-path", default=GODOT_DEFAULT_PATH, help="Ruta al ejecutable de Godot")
    parser.add_argument("--trigger-import", action="store_true", help="Dispara Godot headless tras mover el archivo para registrar UID")

    args = parser.parse_args()
    
    input_mesh = Path(args.input)
    if not input_mesh.exists():
        print(f"[!] Error: El archivo de entrada no existe: {input_mesh}")
        sys.exit(1)
        
    # Determinar ruta GLB temporal
    mesh_stem = input_mesh.stem
    temp_dir = Path("tmp_pipeline_export")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_glb = temp_dir / f"{mesh_stem}_repaired.glb"
    
    # Preparar argumentos para Blender Bridge
    bridge_args = [
        "--mesh", str(input_mesh.resolve()),
        "--output", str(temp_glb.resolve()),
        "--format", "glb"
    ]
    
    if not args.no_apply_transforms:
        bridge_args.append("--apply-transforms")
    if not args.no_sanitize:
        bridge_args.append("--sanitize-geometry")
    if not args.no_normalize_pivot:
        bridge_args.append("--normalize-pivot")
    if args.clean_vertex_colors:
        bridge_args.append("--clean-vertex-colors")
    if args.albedo:
        bridge_args.extend(["--albedo", str(Path(args.albedo).resolve())])
    if args.normal:
        bridge_args.extend(["--normal", str(Path(args.normal).resolve())])
    if args.roughness:
        bridge_args.extend(["--roughness", str(Path(args.roughness).resolve())])
    if args.metallic:
        bridge_args.extend(["--metallic", str(Path(args.metallic).resolve())])
    if args.orm:
        bridge_args.extend(["--orm", str(Path(args.orm).resolve())])
    if args.invert_normal_y:
        bridge_args.append("--invert-normal-y")
    if args.two_sided:
        bridge_args.append("--two-sided")
    if args.alpha_scissor is not None:
        bridge_args.extend(["--alpha-scissor", str(args.alpha_scissor)])
        
    # Paso 1: Blender Headless Repair & Export
    run_blender_process(args.blender_path, bridge_args)
    
    if not temp_glb.exists():
        print(f"[!] Error: No se generó el archivo esperado: {temp_glb}")
        sys.exit(1)
        
    final_dest = temp_glb
    textures_to_copy = [args.albedo, args.normal, args.roughness, args.metallic, args.orm]
    
    # Paso 2: Ingesta en Godot
    if args.project:
        project_dir = Path(args.project)
        if not project_dir.exists():
            print(f"[!] Error: El directorio del proyecto Godot no existe: {project_dir}")
            sys.exit(1)
        final_dest = ingest_to_godot(temp_glb, project_dir, args.category, textures_to_copy)
        
        # Paso 3: Disparo de importación en Godot
        if args.trigger_import:
            trigger_godot_reimport(args.godot_path, project_dir)
            
    elif args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(temp_glb), str(out_p))
        final_dest = out_p
        print(f"[✓] Modelo reparado guardado en: {final_dest}")
    else:
        print(f"[✓] Modelo reparado disponible en: {final_dest}")
        
    print("\n========================================================")
    print(f"[🎉] PIPELINE 3D COMPLETADO EXITOSAMENTE:")
    print(f"     Malla Origen:  {input_mesh.name}")
    print(f"     Destino Final: {final_dest}")
    print("========================================================")

if __name__ == "__main__":
    main()
