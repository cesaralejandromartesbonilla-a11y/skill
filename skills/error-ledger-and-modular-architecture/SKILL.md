---
name: error-ledger-and-modular-architecture
description: Registro formal de errores previos (causa raíz y soluciones) y arquitectura modular desacoplada para prevenir código espagueti.
---

# Error Ledger & Modular Architecture

Sistema para control de errores y arquitectura desacoplada:

1. **Error Ledger:** Antes de diagnosticar o proponer un parche, consulta el catálogo formal de casos resueltos en:
   - [Docs/error_ledger/index.md](file:///c:/Users/cesar/Desktop/skill/Docs/error_ledger/index.md) (Casos ERR-001 al ERR-004 documentados con causas y soluciones).
   - Registra todo nuevo fallo relevante en ese archivo y en `claude-mem` (`save_memory`).

2. **Arquitectura Modular Estricta:**
   - [Docs/architecture/modular_rules.md](file:///c:/Users/cesar/Desktop/skill/Docs/architecture/modular_rules.md)
   - Límite de 250-300 líneas por script.
   - Separación de capas: Input, FSM, Kinematics y Rendering.
   - Señales de abajo hacia arriba (`signal`); llamadas directas de arriba hacia abajo (`call`).
