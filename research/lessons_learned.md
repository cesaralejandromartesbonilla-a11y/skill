# Biblioteca de Lecciones Aprendidas (Experience Reflector)
> **Propósito:** Registro centralizado y vivo de patrones de diseño probados, trampas operativas comunes (*anti-patterns*), modos de fallo observados y decisiones de arquitectura tomadas en el hub `c:\Users\cesar\Desktop\skill`.
> **Inspiración:** Bucle de aprendizaje continuo y memoria recursiva de **Google Research Harness²**.

---

## 1. Entrada y Salida en Entornos Windows (Encoding & Buffers)

### Incidente / Fallo Observado:
- Al ejecutar herramientas de terminal en Windows (`search_ecosystem.py`, `sync_roadmaps.py`, `validate_skill.py`), las impresiones de caracteres Unicode (emojis de estrellas `⭐`, barras de progreso `█`, `░`, o caracteres especiales de caja `│`, `─`) arrojaban la excepción:
  ```
  UnicodeEncodeError: 'charmap' codec can't encode character '\u2b50' in position 12: character maps to <undefined>
  ```
- Posteriormente, al re-envolver `sys.stdout.buffer` con `io.TextIOWrapper` en múltiples scripts encadenados, se produjo:
  ```
  ValueError: I/O operation on closed file.
  ```

### Causa Raíz:
- La consola estándar de Windows (PowerShell / CMD) usa por defecto la página de códigos CP1252 o CP850.
- Crear una nueva instancia de `io.TextIOWrapper` sobre `sys.stdout.buffer` desconecta o cierra el wrapper anterior al ser garbage-collected.

### Patrón de Solución Probado:
Utilizar siempre la API nativa de reconfiguración in-place disponible desde Python 3.7+:
```python
import sys

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```
*Regla de Oro:* Nunca crear nuevos envoltorios de buffer si `reconfigure` está disponible.

---

## 2. Gestión de Dependencias Externas y Clonación Git

### Incidente / Fallo Observado:
- El comando `git clone` y el CLI `npx skills add thedotmack/claude-mem` se congelaban indefinidamente en segundo plano, consumiendo tiempo y ancho de banda.

### Causa Raíz:
- Ciertos repositorios de GitHub acumulan blobs binarios, commits antiguos o ramas experimentales que exceden cientos de megabytes (el historial de `claude-mem` pesa más de 660 MB).

### Patrón de Solución Probado:
1. **Inspeccionar NPM antes de clonar:** Muchos paquetes publican releases empaquetados ultraligeros. En el caso de `claude-mem`, el paquete de npm pesa solo 25.9 MB frente a los 660 MB del repositorio git.
2. **Clonación Superficial Obligatoria:** Si la clonación es indispensable, ejecutar siempre con `--depth 1 --single-branch`:
   ```bash
   git clone --depth 1 --single-branch https://github.com/usuario/repo.git
   ```
3. **Instalador Específico:** Para `claude-mem`, el método óptimo fue `npx -y claude-mem antigravity-cli install`, tardando 3 segundos.

---

## 3. Prevención de Polución por Multi-Agent CLIs

### Incidente / Fallo Observado:
- Al ejecutar comandos comunitarios de skills como `npx skills add DietrichGebert/ponytail --all --copy`, se crearon automáticamente más de 70 carpetas ocultas en la raíz del proyecto (`.adal/`, `.bob/`, `.cline/`, `.cortex/`, `.roo/`, `.supermaven/`, etc.).

### Causa Raíz:
- Los gestores de skills multi-harness intentan por defecto distribuir archivos de configuración para todos los clientes de IA conocidos si no se restringe el objetivo.

### Patrón de Solución Probado:
- Especificar siempre el target de harness: `--agent antigravity` o `--agent claude-code`.
- Mantener un script o procedimiento de limpieza en Git para restaurar la raíz limpia inmediatamente:
  ```powershell
  Get-ChildItem -Directory -Hidden | Where-Object { $_.Name -notin @('.git', '.agents') } | Remove-Item -Recurse -Force
  ```

---

## 4. Pipeline de Conversión 3D Headless en Blender 5.0

### Hallazgos de API y Arquitectura:
1. **Slotted Actions (Animación 2025):**
   - Blender 5.0 abandonó el modelo de `action.fcurves` planos asignados directamente al objeto. Ahora las animaciones usan capas jerárquicas y *slots* (`action.slots`). Para vincular acciones en scripts Python se debe usar:
     ```python
     if hasattr(armature.animation_data, "action"):
         armature.animation_data.action = new_action
     ```
2. **Inversión de Espacios Normales (DirectX vs OpenGL):**
   - Unreal Engine y Unity exportan o calculan mapas de normales con el eje Y invertido (DirectX). Blender requiere el estándar OpenGL (verde hacia arriba).
   - *Solución Determinista:* El script `tools/blender_universal_bridge.py` inserta un nodo de inversión de canal RGB (`Invert Color`) en el canal Green antes de conectar la textura al shader Principled BSDF.
3. **Mallas Poligonales y Shading Suave:**
   - En Blender 5.0, el operador clásico `bpy.ops.object.shade_smooth()` requiere selección en contexto. En modo headless batch, es preferible iterar sobre los polígonos:
     ```python
     for poly in mesh.polygons:
         poly.use_smooth = True
     ```

---

## 5. Optimización de Descubrimiento de Skills (SDO)

### La Trampa del Resumen de Flujo (*Workflow Spoiler*):
- **Problema Descubierto:** Si la `description` en el frontmatter de una skill resume las etapas operativas (ej. *"Use when doing TDD - writes failing test first, then minimal code, then refactors"*), los modelos de LLM tienden a ejecutar esa síntesis directamente en lugar de invocar y leer el documento `SKILL.md` completo.
- **Impacto:** Se omiten validaciones críticas, listas de control y flujos de revisión en dos etapas definidos en el cuerpo.
- **Regla Estricta:**
  - La descripción debe indicar **únicamente las condiciones disparadoras y síntomas**, nunca el flujo interno.
  - Debe comenzar siempre con `"Use when..."`.
  - Debe mantenerse preferentemente por debajo de los 500 caracteres.

---

## 6. Seguridad y Aislamiento en Servidores MCP

### Riesgos Identificados:
- Los servidores MCP que exponen herramientas de ejecución arbitraria de comandos (`shell_execute`) o acceso sin restricciones a lectura/escritura de archivos representan una superficie de ataque crítica si se conectan directamente a credenciales de producción.

### Protocolo de Mitigación:
1. **Catálogo Formal:** Todo MCP debe registrarse primero en `mcp/catalog.json` con su nivel de riesgo y permisos explícitos.
2. **Auditoría de Seguridad:** Completar la plantilla `mcp/templates/MCP_AUDIT.template.md` antes de habilitarlo globalmente.
3. **Sandbox con Mocking:** Utilizar `tools/sandbox_runner.py` con `vercel-labs/emulate` para simular APIs de terceros (GitHub, Slack, Stripe, AWS) en un entorno local y controlado antes de conectar APIs reales.

---

## 7. Mantenimiento de Hojas de Ruta Duales (Dual-Roadmap)

### Principio Operativo:
- El roadmap técnico exhaustivo (`ROADMAP_DETAILED.md`) y el resumen visual para ejecutivos (`ROADMAP_EXECUTIVE.md`) no deben divergir manualmente.
- Tras completar o redefinir cualquier tarea en el archivo detallado, se debe ejecutar inmediatamente:
  ```powershell
  python skills/dual-roadmap/scripts/sync_roadmaps.py ROADMAP_DETAILED.md
  ```
- Esto recalcula automáticamente las barras de progreso, porcentajes de avance por fase y actualiza la matriz en el documento ejecutivo.
