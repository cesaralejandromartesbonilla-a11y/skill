# Informe de Auditoría y Dogfooding Web

> **URL Objetivo:** `{TARGET_URL}`  
> **Fecha de Evaluación:** `{DATE}`  
> **Sesión de Navegación:** `{SESSION_NAME}`  
> **Auditor:** Agente Automatizado (`agent-browser`)  

---

## 1. Resumen Ejecutivo de Hallazgos

| Severidad | Cantidad | Descripción del Impacto |
| :--- | :---: | :--- |
| **Crítica (Critical)** | 0 | Bloqueo total de funcionalidad principal o error 500 no recuperable. |
| **Alta (High)** | 0 | Fallo severo en flujos de conversión, formularios o navegación rota. |
| **Media (Medium)** | 0 | Defectos de maquetación, desalineación o errores de consola en segundo plano. |
| **Baja (Low)** | 0 | Errores ortográficos, textos de marcador de posición (placeholder) o detalles cosméticos. |
| **Total Incidentes** | **0** | Hallazgos verificados y reproducibles con evidencia. |

---

## 2. Registro Detallado de Incidentes

<!-- Plantilla para cada incidente descubierto -->

### ISSUE-001: [Título Conciso del Problema]
- **Severidad:** `[Critical | High | Medium | Low]`
- **Ubicación / URL:** `{PAGE_URL}`
- **Elemento Afectado:** `[@ref / Selector]`
- **Síntoma Observado:** Descripción clara de lo que ocurre versus lo esperado.
- **Pasos para Reproducir:**
  1. Navegar a `{URL}`.
  2. Ejecutar click en `[@eX]`.
  3. Observar el estado de error.
- **Evidencia Gráfica:** `screenshots/issue-001.png`
- **Registro de Consola / Red:**
  ```text
  [Console / Network error log if applicable]
  ```

---

## 3. Registro de Rendimiento y Huella de Navegación
- **Nodos Accesibles Auditados:** `{TOTAL_NODES}`
- **Páginas Recorridas:** `{TOTAL_PAGES}`
- **Tiempo de Sesión:** `{SESSION_DURATION}`
