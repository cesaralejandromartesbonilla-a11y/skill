# EVALUACIÓN DE REPOSITORIOS: LOTE 2 (HERRAMIENTAS Y SKILLS AVANZADAS)

> **Fecha:** 2026-10-25  
> **Repositorios Evaluados:**
> 1. `vercel-labs/emulate`
> 2. `DietrichGebert/ponytail`
> 3. `obra/superpowers`
> 4. `vercel-labs/agent-browser`

---

## 1. Visión Global del Lote

Este cuarteto de repositorios expande radicalmente las capacidades operativas de los agentes en cuatro frentes críticos:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MAPA DE CAPACIDADES (LOTE 2)                    │
├────────────────────────────────┬───────────────────────────────────────┤
│  1. DISCIPLINA Y RIGOR         │  2. ENFOQUE MINIMALISTA (YAGNI)       │
│     obra/superpowers           │     DietrichGebert/ponytail           │
│  • Metodología TDD             │  • "Senior Dev Perezoso"              │
│  • Generación de skills        │  • Mínimo código posible              │
│  • Verificación con evidencia  │  • Uso de librerías estándar          │
├────────────────────────────────┼───────────────────────────────────────┤
│  3. SIMULACIÓN Y SANDBOX       │  4. NAVEGACIÓN Y WEB HEADLESS         │
│     vercel-labs/emulate        │     vercel-labs/agent-browser         │
│  • Mocks locales con estado    │  • Árbol de accesibilidad (@e1, @e2)  │
│  • 14 APIs (Stripe, AWS, etc.) │  • Ahorro drástico de tokens (>90%)   │
│  • Sin gastar cuota/credenciales│ • Automatización de Electron y React  │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Análisis Detallado por Repositorio

### A. `vercel-labs/emulate`
- **URL:** [https://github.com/vercel-labs/emulate](https://github.com/vercel-labs/emulate)
- **Organización:** Vercel Labs
- **Categoría:** Herramienta CLI / Servidor Mock Local con Estado (`npx emulate`).
- **Problema que resuelve:** Cuando un agente o desarrollador prueba herramientas o integra APIs de terceros (Stripe, GitHub, AWS S3/SQS, Slack, Twilio), suele requerir credenciales reales, tokens de prueba en la nube, conexión a internet y arriesgar cuotas o costos.
- **Capacidades Clave:**
  - **Servicios Soportados Out-of-the-Box:** `stripe`, `github`, `aws`, `slack`, `google`, `microsoft`, `apple`, `okta`, `resend`, `mongoatlas`, `clerk`, `linear`, `twilio`, `vercel`.
  - **Estado Persistente:** Si el agente crea un repositorio en GitHub o procesa un cargo en Stripe a través del emulador local, el recurso queda registrado en la base de datos mock local para peticiones posteriores.
  - **Protocolos Reales:** Emula flujos OAuth con tokens RS256, respuestas XML de AWS, paginación con cursores y firmas de Webhooks (ej. `Stripe-Signature`, `X-Slack-Signature`).
- **Aplicabilidad en el Hub:** Ideal para probar nuevos servidores MCP o herramientas sin exponer llaves API privadas ni consumir saldo de servicios en la nube.

---

### B. `DietrichGebert/ponytail`
- **URL:** [https://github.com/DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)
- **Autor:** Dietrich Gebert
- **Categoría:** Suite de Skills para Agentes (`ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review`).
- **Problema que resuelve:** Los LLMs tienden al sobre-diseño (*over-engineering*), añadiendo dependencias innecesarias, código repetitivo o abstracciones complejas.
- **Filosofía Clave:** *"The best code is the code you never wrote"*.
  - **Principio YAGNI (You Aren't Gonna Need It):** Elimina cualquier flexibilidad o configuración que no haya sido expresamente solicitada.
  - **Prioridad a lo Existente:** Fuerza a usar bibliotecas estándar del lenguaje antes de sugerir instalar un paquete nuevo.
  - **Transparencia de Riesgos:** Al finalizar cada respuesta, resume obligatoriamente qué cosas se omitieron y los riesgos técnicos asociados.
  - **Niveles de Intensidad:** `lite`, `full` (predeterminado), y `ultra`.
- **Estado en el Hub:** Adoptado e integrado en `skills/ponytail*`.

---

### C. `obra/superpowers`
- **URL:** [https://github.com/obra/superpowers](https://github.com/obra/superpowers)
- **Autor:** Jesse Vincent (`obra`)
- **Categoría:** Framework Metodológico y Suite de 15 Skills de Ingeniería de Software para Agentes.
- **Problema que resuelve:** Evita que los agentes de programación trabajen a ciegas o afirmen que una tarea está resuelta sin haber ejecutado pruebas o comprobaciones reales.
- **Skills Destacadas:**
  1. `writing-skills`: Guía maestra para crear, estructurar y validar nuevas skills antes de desplegarlas (fundamental para la misión de este repositorio).
  2. `test-driven-development`: Fuerza la metodología TDD (escribir primero la prueba que falla antes de tocar el código de implementación).
  3. `verification-before-completion`: Prohíbe terminantemente afirmar éxito sin evidencia ejecutable.
  4. `using-git-worktrees`: Aislamiento estricto de experimentos en ramas y worktrees independientes.
  5. `dispatching-parallel-agents`: Orquestación de subagentes en paralelo para tareas sin dependencias mutuas.
- **Estado en el Hub:** Skills nucleares adoptadas en `skills/`.

---

### D. `vercel-labs/agent-browser`
- **URL:** [https://github.com/vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)
- **Organización:** Vercel Labs
- **Categoría:** CLI de Automatización de Navegador Diseñado Específicamente para Agentes de IA.
- **Problema que resuelve:** Los navegadores tradicionales (Selenium, Playwright crudo) entregan árboles DOM masivos en HTML que saturan el contexto del LLM (decenas de miles de tokens) y confunden la toma de decisiones.
- **Mecanismo Revolucionario:**
  - **Árbol de Accesibilidad Simplificado:** Transforma la página web en un árbol de elementos interactivos con identificadores cortos (`@e1`, `@e2`, `@e3`).
  - **Comandos Deterministas:** El agente interactúa directamente usando las referencias: `agent-browser click @e2`, `agent-browser fill @e3 "texto"`.
  - **Capturas Anotadas:** `agent-browser screenshot --annotate` superpone etiquetas numeradas en la imagen para modelos con visión.
  - **Inspección de React y Electron:** Soporte nativo para recorrer árboles de componentes React y automatizar aplicaciones de escritorio basadas en Electron (VS Code, Slack, Discord).
- **Skills Incorporadas:** El propio binario incluye skills integradas (`agent-browser skills get core`, `dogfood`, `electron`).

---

## 3. Acciones de Integración en el Workspace

| Elemento | Destino en el Hub | Estado |
| :--- | :--- | :---: |
| Skills de `ponytail` (6 skills) | `skills/ponytail*` | Instaladas |
| Skills núcleo de `superpowers` (`writing-skills`, `test-driven-development`, etc.) | `skills/writing-skills`, etc. | Instaladas |
| Emulador local de APIs (`emulate`) | Herramienta CLI disponible vía `npx emulate` | Documentado |
| Navegador de agentes (`agent-browser`) | Herramienta CLI disponible vía `npx agent-browser` | Documentado |
