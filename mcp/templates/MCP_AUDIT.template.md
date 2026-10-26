# REPORTE DE AUDITORÍA DE SERVIDOR MCP: {{SERVER_NAME}}

> **Identificador:** `{{SERVER_ID}}`  
> **Fecha de Auditoría:** {{DATE}}  
> **Auditor:** Agente / Usuario  
> **Resultado:** 🟢 Aprobado / 🟡 Con advertencias / 🔴 Rechazado

---

## 1. Ficha Técnica

- **Repositorio:** [{{REPOSITORY_URL}}]({{REPOSITORY_URL}})
- **Paquete / Runtime:** `{{PACKAGE_OR_COMMAND}}`
- **Transporte:** `stdio` / `streamable_http`
- **Categoría:** {{CATEGORY}}
- **Propósito Principal:** {{PURPOSE_SUMMARY}}

---

## 2. Evaluación de Seguridad y Privacidad

| Criterio | Pregunta | Evaluación | Notas |
| :--- | :--- | :---: | :--- |
| **Aislamiento de Archivos** | ¿El servidor puede leer/escribir fuera del directorio designado? | Sí / No / Acotado | {{NOTES_ISOLATION}} |
| **Manejo de Credenciales** | ¿Requiere tokens o contraseñas? ¿Cómo se transmiten? | Seguro / Variable | {{NOTES_CREDENTIALS}} |
| **Ejecución Arbitraria** | ¿Permite ejecución de código arbitrario (RCE) no solicitada? | No detectado / Sí | {{NOTES_RCE}} |
| **Comportamiento de Red** | ¿Realiza llamadas a servidores remotos no documentados? | Auditado / No | {{NOTES_NETWORK}} |

---

## 3. Inventario de Herramientas Expuestas

| Herramienta | Parámetros Principales | Nivel de Riesgo | Uso Permitido |
| :--- | :--- | :---: | :--- |
| `{{TOOL_1}}` | `{{PARAMS_1}}` | Bajo / Medio / Alto | {{USAGE_1}} |
| `{{TOOL_2}}` | `{{PARAMS_2}}` | Bajo / Medio / Alto | {{USAGE_2}} |

---

## 4. Pruebas en Sandbox Local (`emulate`)

- [ ] Servidor iniciado en modo aislado sin internet.
- [ ] Esquema JSON verificado sin errores sintácticos.
- [ ] Tiempo de respuesta de herramientas inferior a 500ms.

---

## 5. Dictamen y Configuración Recomendada

```json
{
  "mcpServers": {
    "{{SERVER_ID}}": {
      "command": "{{COMMAND}}",
      "args": ["{{ARGS}}"],
      "env": {}
    }
  }
}
```
