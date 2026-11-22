# Plan Maestro: Reducción del 70% del Costo de Tokens en Skills y Arquitectura `Docs/`

> **Fecha:** 21 de Noviembre de 2026  
> **Workspace:** `c:\Users\cesar\Desktop\skill`  
> **Métrica Objetivo:** Reducir el consumo de ~9,500 tokens a <5,000 tokens (alcanzable: ~2,500 tokens).

---

## 1. Diagnóstico Empírico: De Dónde se Esfumaban los Tokens

Ejecutamos una auditoría automatizada en tiempo real mediante [`tools/audit_skills_tokens.py`](file:///c:/Users/cesar/Desktop/skill/tools/audit_skills_tokens.py) escaneando todos los directorios de skills del sistema:
- `c:\Users\cesar\Desktop\skill\.agents\skills`
- `c:\Users\cesar\Desktop\skill\skills`
- `C:\Users\cesar\.gemini\config\plugins\global-mcp-skills-hub\skills`
- `C:\Users\cesar\.gemini\config\plugins\godot-prompter\skills`
- `C:\Users\cesar\.gemini\config\skills`

### Resultados del Escaneo Inicial:
- **Total de instancias de skills cargadas:** 149 carpetas.
- **Caracteres inyectados en el catálogo de prompt:** **31,600 caracteres**.
- **Tokens consumidos por turno (solo en listar skills):** **~7,800 a 9,500 tokens**.
- **Skills únicas:** 94.
- **Skills duplicadas / triplicadas / cuadruplicadas:** **34 skills**.

---

## 2. Los Tres Pilares de Optimización

1. **Deduplicación Física:** Eliminar copias espejo en directorios duplicados.
2. **Descripciones Lean:** Regla de <= 120 caracteres por skill sin ejemplos irrelevantes en frontmatter.
3. **Fusiones:** Agrupar micro-skills por dominios lógicos (Ponytail 6-en-1, Godot pares, Superpowers workflows).

---

## 3. Implementación de la Arquitectura `Docs/` y Punteros Progresivos

- Directorio central creado: [`Docs/master_index.md`](file:///c:/Users/cesar/Desktop/skill/Docs/master_index.md).
- Skill puntero creada: [`.agents/skills/workspace-docs-navigator/SKILL.md`](file:///c:/Users/cesar/Desktop/skill/.agents/skills/workspace-docs-navigator/SKILL.md) (~33 tokens).
- Desacoplamiento de Error Ledger en [`Docs/error_ledger/index.md`](file:///c:/Users/cesar/Desktop/skill/Docs/error_ledger/index.md).
