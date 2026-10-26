#!/usr/bin/env python3
"""
Unity Asset Extractor (Headless CLI)
Extrae mallas (Mesh -> OBJ/GLTF), texturas (Texture2D -> PNG), clips de audio y datos
desde archivos .assets, .unity3d y AssetBundles para uso en Blender 5.0.

Uso:
    python tools/unity_asset_extractor.py list <input_file_or_dir>
    python tools/unity_asset_extractor.py extract <input_file_or_dir> --output <out_dir> [--types Mesh Texture2D]
"""

import os
import sys
import argparse
from pathlib import Path

# Configurar salida UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def get_unitypy():
    try:
        import UnityPy
        return UnityPy
    except ImportError:
        print("[!] Error: UnityPy no está instalado. Ejecuta: pip install UnityPy Pillow")
        sys.exit(1)

def list_assets(target_path: str, filter_type: str = None):
    UnityPy = get_unitypy()
    env = UnityPy.load(target_path)
    
    counts = {}
    print(f"[*] Inspeccionando activos en: {target_path}\n")
    print(f"| ID/PathID | Tipo | Nombre | Tamaño/Info |")
    print(f"| :--- | :--- | :--- | :--- |")
    
    total = 0
    for obj in env.objects:
        type_name = obj.type.name
        counts[type_name] = counts.get(type_name, 0) + 1
        
        if filter_type and type_name.lower() != filter_type.lower():
            continue
            
        data = obj.read()
        name = getattr(data, "name", getattr(data, "m_Name", f"unnamed_{obj.path_id}"))
        extra = ""
        if type_name == "Texture2D":
            extra = f"{getattr(data, 'm_Width', '?')}x{getattr(data, 'm_Height', '?')}"
        elif type_name == "Mesh":
            submeshes = len(getattr(data, "submeshes", []))
            extra = f"Submeshes: {submeshes}"
            
        print(f"| {obj.path_id} | {type_name} | {name} | {extra} |")
        total += 1
        if total >= 50 and not filter_type:
            print(f"\n[i] Mostrando los primeros 50 activos. Usa --type para filtrar específicamente.")
            break
            
    print("\n--- Resumen de Clases Encontradas ---")
    for k, v in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {k}: {v}")

def export_mesh_to_obj(mesh_data, out_path: Path):
    """Exporta un objeto Mesh de Unity a un archivo .obj compatible con Blender."""
    vertices = getattr(mesh_data, "m_Vertices", [])
    normals = getattr(mesh_data, "m_Normals", [])
    uvs = getattr(mesh_data, "m_UV0", [])
    indices = getattr(mesh_data, "m_Indices", [])
    
    if not vertices:
        return False
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Unity Mesh: {mesh_data.name}\n")
        f.write(f"o {mesh_data.name}\n")
        
        # Escribir vértices (Invertir X si se desea compensar el sistema de coordenadas de Unity)
        for v in vertices:
            f.write(f"v {-v.x:.6f} {v.y:.6f} {v.z:.6f}\n")
            
        # Escribir coordenadas de textura (UV)
        for uv in uvs:
            f.write(f"vt {uv.x:.6f} {uv.y:.6f}\n")
            
        # Escribir normales
        for n in normals:
            f.write(f"vn {-n.x:.6f} {n.y:.6f} {n.z:.6f}\n")
            
        # Escribir caras (triángulos)
        has_uv = len(uvs) > 0
        has_n = len(normals) > 0
        
        for i in range(0, len(indices), 3):
            if i + 2 < len(indices):
                # Unity usa orientación de reloj opuesta a OBJ por el cambio de mano
                i1, i2, i3 = indices[i] + 1, indices[i+2] + 1, indices[i+1] + 1
                if has_uv and has_n:
                    f.write(f"f {i1}/{i1}/{i1} {i2}/{i2}/{i2} {i3}/{i3}/{i3}\n")
                elif has_uv:
                    f.write(f"f {i1}/{i1} {i2}/{i2} {i3}/{i3}\n")
                elif has_n:
                    f.write(f"f {i1}//{i1} {i2}//{i2} {i3}//{i3}\n")
                else:
                    f.write(f"f {i1} {i2} {i3}\n")
    return True

def extract_assets(target_path: str, output_dir: str, types=None, name_filter=None):
    UnityPy = get_unitypy()
    env = UnityPy.load(target_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    target_types = set([t.lower() for t in types]) if types else {"mesh", "texture2d", "audioclip", "textasset"}
    extracted_counts = {}
    
    print(f"[*] Extrayendo activos desde: {target_path}")
    print(f"[*] Directorio de salida: {out_dir.resolve()}")
    print(f"[*] Tipos objetivo: {', '.join(target_types)}\n")
    
    for obj in env.objects:
        type_name = obj.type.name
        if type_name.lower() not in target_types:
            continue
            
        try:
            data = obj.read()
            name = getattr(data, "name", getattr(data, "m_Name", f"unnamed_{obj.path_id}"))
            if not name:
                name = f"asset_{obj.path_id}"
                
            # Limpiar nombre para sistema de archivos
            safe_name = "".join([c if c.isalnum() or c in "._- " else "_" for c in name])
            
            if name_filter and name_filter.lower() not in safe_name.lower():
                continue
                
            type_folder = out_dir / type_name
            type_folder.mkdir(exist_ok=True)
            
            if type_name == "Texture2D":
                img = data.image
                if img:
                    img_path = type_folder / f"{safe_name}.png"
                    img.save(img_path)
                    extracted_counts["Texture2D"] = extracted_counts.get("Texture2D", 0) + 1
            elif type_name == "Mesh":
                # Intentar usar el exportador OBJ incorporado o el manual
                obj_path = type_folder / f"{safe_name}.obj"
                success = False
                if hasattr(data, "export"):
                    try:
                        res = data.export()
                        with open(obj_path, "wb") as f:
                            f.write(res.encode("utf-8") if isinstance(res, str) else res)
                        success = True
                    except Exception:
                        success = False
                if not success:
                    success = export_mesh_to_obj(data, obj_path)
                if success:
                    extracted_counts["Mesh"] = extracted_counts.get("Mesh", 0) + 1
            elif type_name == "AudioClip":
                for sample_name, sample_bytes in data.samples.items():
                    audio_path = type_folder / f"{sample_name}"
                    with open(audio_path, "wb") as f:
                        f.write(sample_bytes)
                    extracted_counts["AudioClip"] = extracted_counts.get("AudioClip", 0) + 1
            elif type_name == "TextAsset":
                script_path = type_folder / f"{safe_name}.txt"
                with open(script_path, "wb") as f:
                    f.write(data.script)
                extracted_counts["TextAsset"] = extracted_counts.get("TextAsset", 0) + 1
        except Exception as e:
            # Continuar en caso de activos corruptos o clases no serializables
            continue
            
    print("\n[+] Extracción completada con éxito:")
    for k, v in extracted_counts.items():
        print(f"  - {k}: {v} archivos guardados")

def main():
    parser = argparse.ArgumentParser(description="Unity Asset Extractor for Blender 5.0")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcomando list
    list_parser = subparsers.add_parser("list", help="Lista los objetos dentro del archivo de Unity")
    list_parser.add_argument("input", help="Ruta al archivo .assets, .bundle o carpeta")
    list_parser.add_argument("--type", help="Filtrar por tipo de clase (ej. Mesh, Texture2D)")
    
    # Subcomando extract
    extract_parser = subparsers.add_parser("extract", help="Extrae activos convertidos")
    extract_parser.add_argument("input", help="Ruta al archivo .assets, .bundle o carpeta")
    extract_parser.add_argument("--output", "-o", default="extracted_unity", help="Directorio de salida")
    extract_parser.add_argument("--types", "-t", nargs="+", help="Tipos a extraer (ej. Mesh Texture2D)")
    extract_parser.add_argument("--filter", "-f", help="Filtrar por coincidencia en el nombre")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_assets(args.input, args.type)
    elif args.command == "extract":
        extract_assets(args.input, args.output, args.types, args.filter)

if __name__ == "__main__":
    main()
