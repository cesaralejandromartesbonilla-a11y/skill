---
name: dual-roadmap
description: Use when planning, tracking, or updating project roadmaps, requiring both an exhaustive, continuously updated living technical roadmap and a concise, visual executive summary for fast reading.
license: MIT
metadata:
  version: "1.0"
  author: "Skill Hub"
---

# Dual-Track Roadmap: Hojas de Ruta Técnica y Ejecutiva

Esta skill establece la metodología y los estándares para generar y mantener **dos hojas de ruta complementarias e interconectadas** para cualquier proyecto o desarrollo:

1. **Hoja de Ruta Exhaustiva y Viva (`ROADMAP_DETAILED.md`)**: Registro técnico milimétrico, granular y continuo. Se actualiza con cada cambio, tarea o decisión.
2. **Hoja de Ruta Resumida y Visual (`ROADMAP_EXECUTIVE.md`)**: Cuadro de mando ejecutivo, vistoso y directo (máximo 1 pantalla). Destaca únicamente el progreso visual, hitos clave y prioridades inmediatas.

---

## 1. Arquitectura de Dos Vías (Dual-Track)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CICLO DE ACTUALIZACIÓN DUAL                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [Avance de Trabajo / Nueva Tarea / Corrección / Cambio de Rumbo]    │
│                                │                                       │
│                                ▼                                       │
│     1. ACTUALIZAR DETALLE TÉCNICO (`ROADMAP_DETAILED.md`)              │
│        • Marcar [X] tareas completadas / [/] en progreso               │
│        • Añadir nuevos sub-pasos o dependencias descubiertas           │
│        • Anotar riesgos, archivos afectados o deuda técnica            │
│                                │                                       │
│                                ▼                                       │
│     2. SINCRONIZAR VISTA EJECUTIVA (`ROADMAP_EXECUTIVE.md`)            │
│        • Recalcular porcentajes y barra de progreso                    │
│        • Actualizar el estado del Hito actual ("Dónde estamos")        │
│        • Ajustar el Top 3 de prioridades inmediatas                    │
│        • Refrescar el semáforo de salud del proyecto                   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Artefacto 1: Hoja de Ruta Exhaustiva (`ROADMAP_DETAILED.md`)

Este documento es la **fuente de la verdad operativa**. Ningún detalle técnico se omite.

### Reglas Obligatorias:
- **Estructura WBS (Work Breakdown Structure):** Todo el trabajo se divide en Fases (`F1`, `F2`), Épicas e Hitos numerados con IDs únicos (ej. `[F1-T04]`).
- **Estados de Tarea:**
  - `[ ]` **Pendiente:** Planificada pero no iniciada.
  - `[/]` **En Progreso:** Trabajo activo en la sesión actual.
  - `[X]` **Completada:** Terminada y verificada con pruebas o evidencia.
  - `[-]` **Descartada / Postergada:** Explicada en la bitácora con motivo.
- **Campos por Tarea Crítica:**
  - *Dependencias:* Qué tareas deben terminar antes de iniciar.
  - *Archivos o Módulos:* Rutas directas en el repositorio.
  - *Criterio de Aceptación (DoD):* Cómo se prueba que funciona.
- **Sección de Deuda Técnica y Atajos:** Espacio para registrar cosas postergadas a propósito para no perder momentum.
- **Bitácora de Cambios (Change Log del Plan):** Cada vez que se mueve una fecha o se descarta un componente, se anota la razón.

---

## 3. Artefacto 2: Hoja de Ruta Resumida (`ROADMAP_EXECUTIVE.md`)

Este documento está diseñado para ser **leído en menos de 60 segundos** por el usuario, líderes o colaboradores.

### Reglas Obligatorias:
- **Cero Micro-Gestión:** Prohibido listar tareas de 5 minutos, commits individuales o detalles internos de implementación.
- **Elementos Visuales Obligatorios:**
  - **Barra de Progreso Gráfica:**
    ```text
    Fase 1: Motor Base        [██████████] 100% (Completado)
    Fase 2: Interfaz Visual   [██████░░░░]  60% (En curso)
    Fase 3: Optimización      [░░░░░░░░░░]   0% (Pendiente)
    Total del Proyecto        [█████░░░░░]  53%
    ```
  - **Semáforo de Salud:**
    - 🟢 **En tiempo / Saludable:** Sin bloqueos mayores.
    - 🟡 **Atención:** Riesgo menor o tarea retrasada sin impacto crítico.
    - 🔴 **Bloqueado:** Requiere decisión del usuario o factor externo.
  - **Caja de Enfoque Actual ("¿Dónde estamos hoy?"):**
    - 1 párrafo claro que explica el estado actual del proyecto.
  - **Top 3 Próximos Pasos:**
    - Únicamente las 3 metas más importantes que desbloquean el siguiente hito.
  - **Diagrama Mermaid (Opcional si aporta claridad):** Un diagrama de flujo temporal de alto nivel (`flowchart LR`).

---

## 4. Protocolo de Redacción Paso a Paso

Cuando el usuario solicite crear o planificar una hoja de ruta:

### Paso 1: Descubrimiento y Alcance
1. Identificar el objetivo final del proyecto y los entregables clave.
2. Dividir el proyecto en fases secuenciales (normalmente entre 3 y 5 fases).

### Paso 2: Generar Primero `ROADMAP_DETAILED.md`
1. Crear el archivo detallado desglosando cada fase en tareas atómicas (`[F1-T01]`, etc.).
2. Establecer dependencias y criterios de verificación.
3. Marcar el estado inicial de cada tarea.

### Paso 3: Sintetizar `ROADMAP_EXECUTIVE.md`
1. Calcular el total de tareas por fase para construir la barra de progreso.
2. Extraer los hitos mayores y redactar el estado de salud y el foco actual.
3. Asegurar que no supere 60-80 líneas en total.

### Paso 4: Mantenimiento Continuo (Regla de Oro)
- Al completar una tarea en el código:
  1. Actualizar `ROADMAP_DETAILED.md` marcando `[X]` y añadiendo notas si hubo variaciones.
  2. Actualizar la barra de progreso y el foco en `ROADMAP_EXECUTIVE.md`.
  3. Informar al usuario en la respuesta con un enlace a ambos documentos.

---

## 5. Scripts de Soporte

La skill incluye el script auxiliar [`scripts/sync_roadmaps.py`](scripts/sync_roadmaps.py) para automatizar el recuento de tareas `[X]` frente a `[ ]` y calcular el porcentaje exacto de completitud entre ambos documentos.
