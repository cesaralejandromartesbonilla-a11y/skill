import os
import glob
import re

updates = {
    "verification-before-completion": "Verificación estricta con evidencia empírica (comandos y pruebas) antes de declarar éxito o crear PRs.",
    "receiving-code-review": "Evaluación crítica y verificación técnica del feedback de revisión antes de implementar sugerencias.",
    "brainstorming": "Exploración creativa inicial, definición de requisitos y alternativas antes de planificar o codificar.",
    "using-git-worktrees": "Aislamiento de tareas y ramas independientes mediante git worktrees en el espacio de trabajo.",
    "dual-roadmap": "Gestión de roadmaps técnicos exhaustivos y resúmenes ejecutivos visuales de alto nivel.",
    "rendering-pipeline": "Selección del renderer, presupuesto de cuadros, iluminación y optimización gráfica en Godot 4.",
    "godot-code-review": "Revisión de código GDScript y C# contra antipatrones, rendimiento y trampas comunes de Godot 4.",
    "csharp-signals": "Implementación de señales en C# para Godot ([Signal], EmitSignal, async ToSignal e interop).",
    "web-services": "Cliente HTTPRequest, APIs REST/JSON, autenticación y WebSockets en juegos Godot 4.",
    "web-export": "Exportación Web (HTML5/Wasm), headers COOP/COEP y despliegue en navegador para Godot 4.",
    "particles-vfx": "Sistemas de partículas GPUParticles2D/3D, ParticleProcessMaterial y efectos visuales en Godot 4.",
    "2d-essentials": "Sistemas 2D en Godot: TileMaps, parallax scrolling, luces 2D, CanvasLayers y custom drawing.",
    "3d-essentials": "Sistemas 3D en Godot: materiales PBR, iluminación, niebla volumétrica, oclusión y decals.",
    "physics-system": "Físicas en Godot: CharacterBody, RigidBody, colisiones, raycasting y resortes 2D/3D.",
    "player-controller": "Controladores de movimiento de personajes 2D/3D con CharacterBody y cinemática en Godot.",
    "camera-system": "Sistemas de cámara 2D/3D: seguimiento suave, screen shake, límites de zona y transiciones.",
    "input-handling": "Mapeo de entradas (Input Map), mandos/gamepads, mouse, pantallas táctiles y rebinding.",
    "animation-system": "Animaciones en Godot: AnimationPlayer, AnimationTree, blend trees, state machines e IK.",
    "state-machine": "Máquinas de estados finitos (FSM) para lógica de juego: patrones enum, nodo y recursos.",
    "inventory-system": "Sistemas de inventario basados en recursos: slots, apilamiento, contenedores y enlace a UI.",
    "ability-system": "Sistema de habilidades: costos, enfriamientos, modificadores de atributos y tags de juego."
}

paths = [
    r'c:\Users\cesar\Desktop\skill\.agents\skills',
    r'c:\Users\cesar\Desktop\skill\skills',
    r'C:\Users\cesar\.gemini\config\skills',
    r'C:\Users\cesar\.gemini\config\plugins\godot-prompter\skills',
    r'C:\Users\cesar\.gemini\config\plugins\global-mcp-skills-hub\skills'
]

count = 0
for p in paths:
    if not os.path.exists(p):
        continue
    for skill_name, new_desc in updates.items():
        smd = os.path.join(p, skill_name, 'SKILL.md')
        if os.path.exists(smd):
            with open(smd, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Replace description
            new_content = re.sub(
                r'^description:\s*(?:>-|>|")?(.*?)(?=\n[a-zA-Z0-9_-]+:|\n---)',
                f'description: {new_desc}\n',
                content,
                flags=re.MULTILINE | re.DOTALL,
                count=1
            )
            if new_content != content:
                with open(smd, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                print(f"Updated {skill_name} in {os.path.basename(p)}")

print(f"\nTotal files updated with lean descriptions: {count}")
