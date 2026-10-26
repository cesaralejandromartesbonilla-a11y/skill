# REPORTE DE AUDITORÍA DE SERVIDOR MCP: Chrome DevTools MCP

> **Identificador:** `chrome-devtools`  
> **Fecha de Auditoría:** 2026-10-26  
> **Auditor:** Agente Antigravity  
> **Resultado:** 🟢 Aprobado para uso local y CI

---

## 1. Ficha Técnica

- **Repositorio:** [https://github.com/ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- **Organización:** Google Chrome DevTools Team (Oficial)
- **Paquete / Runtime:** `chrome-devtools-mcp` (Node.js / npx)
- **Transporte:** `stdio`
- **Categoría:** Depuración Web y Automatización (`debugging`)
- **Propósito Principal:** Proporcionar a agentes de programación control granular sobre una instancia viva de Google Chrome mediante el Chrome DevTools Protocol (CDP) para navegación, análisis de red, inspección de consola y auditoría de rendimiento.

---

## 2. Evaluación de Seguridad y Privacidad

| Criterio | Pregunta | Evaluación | Notas |
| :--- | :--- | :---: | :--- |
| **Aislamiento de Archivos** | ¿El servidor puede leer/escribir fuera del directorio designado? | Acotado | Con la bandera `--isolated`, utiliza un perfil temporal descartable. |
| **Manejo de Credenciales** | ¿Requiere tokens o contraseñas? | Seguro | No requiere API keys; se conecta al binario local de Chrome. |
| **Ejecución Arbitraria** | ¿Permite ejecución de código arbitrario (RCE)? | No detectado | Expone herramientas estructuradas de DevTools; comandos JS acotados a la página activa. |
| **Comportamiento de Red** | ¿Realiza llamadas a servidores remotos no documentados? | Auditado | Telemetría desactivable mediante `CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS=1`. |

---

## 3. Inventario de Herramientas Expuestas

| Herramienta | Parámetros Principales | Nivel de Riesgo | Uso Permitido |
| :--- | :--- | :---: | :--- |
| `navigate_page` | `url`, `timeout` | Bajo | Carga de páginas web para inspección y pruebas. |
| `new_page` / `close_page` | `url`, `pageId` | Bajo | Gestión de pestañas. |
| `fill_form` / `click` | `elements`, `selector` | Bajo | Interacción con formularios y botones de la UI. |
| `inspect_network` / `requests` | `filter`, `includeHeaders` | Bajo | Análisis de llamadas a APIs, códigos HTTP y payloads. |
| `read_console_logs` | `types` (error, warn, log) | Bajo | Captura de errores de JavaScript en tiempo de ejecución. |
| `take_screenshot` | `filePath`, `clip` | Bajo | Captura de pantalla para modelos con visión. |
| `performance_start_trace` | `categories` | Bajo | Auditoría de cuellos de botella y rendimiento de renderizado. |

---

## 4. Pruebas y Validación de Configuración

- [X] Configurado para arranque en modo aislado y headless opcional.
- [X] Desactivada la telemetría innecesaria por variables de entorno.
- [X] Configuración empaquetada en `mcp/configs/chrome-devtools.json`.

---

## 5. Configuración Recomendada para Antigravity

```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": [
      "-y",
      "chrome-devtools-mcp@latest",
      "--isolated",
      "--headless"
    ],
    "env": {
      "CHROME_DEVTOOLS_MCP_NO_USAGE_STATISTICS": "1",
      "CHROME_DEVTOOLS_MCP_NO_UPDATE_CHECKS": "1"
    }
  }
}
```
