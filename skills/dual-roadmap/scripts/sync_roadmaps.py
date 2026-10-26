#!/usr/bin/env python3
"""
Dual-Roadmap Synchronizer & Progress Calculator
Lee ROADMAP_DETAILED.md, calcula el recuento de tareas por fase y el porcentaje global,
y genera las barras de progreso visuales para ROADMAP_EXECUTIVE.md.

Uso:
    python skills/dual-roadmap/scripts/sync_roadmaps.py [ruta_detailed] [ruta_executive]
"""

import sys
import re
from pathlib import Path

# Configurar salida UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

def make_bar(percent: float, length: int = 10) -> str:
    """Genera una barra de progreso en texto usando bloques Unicode."""
    filled_len = int(round(length * percent / 100))
    bar = '█' * filled_len + '░' * (length - filled_len)
    return bar

def analyze_detailed(detailed_text: str):
    phases = []
    current_phase = None
    
    lines = detailed_text.splitlines()
    for line in lines:
        phase_match = re.match(r"^###\s+(Fase\s+\d+:\s*[^`\n]+)", line, re.IGNORECASE)
        if phase_match:
            if current_phase:
                phases.append(current_phase)
            current_phase = {
                "name": phase_match.group(1).strip(),
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "discarded": 0,
                "total": 0
            }
            continue
            
        if current_phase:
            # Detectar tareas
            if re.search(r"-\s*\[X\]", line, re.IGNORECASE):
                current_phase["completed"] += 1
                current_phase["total"] += 1
            elif re.search(r"-\s*\[/\]", line):
                current_phase["in_progress"] += 1
                current_phase["total"] += 1
            elif re.search(r"-\s*\[ \]", line):
                current_phase["pending"] += 1
                current_phase["total"] += 1
            elif re.search(r"-\s*\[-\]", line):
                current_phase["discarded"] += 1
                
    if current_phase:
        phases.append(current_phase)
        
    return phases

def generate_report(phases):
    total_tasks = sum(p["total"] for p in phases)
    total_completed = sum(p["completed"] for p in phases)
    total_in_prog = sum(p["in_progress"] for p in phases)
    
    global_pct = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
    
    output = []
    output.append("```text")
    for p in phases:
        pct = (p["completed"] / p["total"] * 100) if p["total"] > 0 else 0
        bar = make_bar(pct, length=10)
        status = "Completado" if pct == 100 else ("En curso" if p["in_progress"] > 0 or p["completed"] > 0 else "Pendiente")
        output.append(f"{p['name'][:30]:<30} [{bar}] {pct:>5.1f}% ({status})")
        
    global_bar = make_bar(global_pct, length=10)
    output.append("-" * 55)
    output.append(f"{'Progreso Total Global':<30} [{global_bar}] {global_pct:>5.1f}%")
    output.append("```")
    return "\n".join(output)

def main():
    detailed_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ROADMAP_DETAILED.md")
    if not detailed_file.exists():
        print(f"[!] No se encontró el archivo: {detailed_file}")
        sys.exit(1)
        
    text = detailed_file.read_text(encoding="utf-8")
    phases = analyze_detailed(text)
    
    if not phases:
        print("[-] No se detectaron fases ni tareas en formato WBS.")
        return
        
    report = generate_report(phases)
    print("\n--- RESUMEN CALCULADO PARA ROADMAP_EXECUTIVE.md ---")
    print(report)

if __name__ == "__main__":
    main()
