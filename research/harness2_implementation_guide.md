# Guía de Implementación del Bucle Harness² (Propose–Probe–Compose)

## 1. Fundamentos Conceptuales de Harness²

El paradigma **Harness²** (propuesto por Google Research en *Harnessing Large Language Models with Harness²*) formaliza el principio de que la inteligencia y adaptabilidad de un agente de IA no reside exclusivamente en los pesos de su modelo fundacional (LLM), sino en la **arquitectura del arnés (harness)** que lo rodea, lo guía y le proporciona herramientas.

Un **arnés** es el sistema socio-técnico completo de software que modula las entradas, restringe las salidas y proporciona el entorno ejecutable para el LLM.

```
       +-----------------------------------------------------------+
       |                     ARQUITECTURA HARNESS                  |
       |                                                           |
       |   +-------------------+          +--------------------+   |
       |   |   System Prompt   |          |    Guardrails      |   |
       |   +-------------------+          +--------------------+   |
       |   +-------------------+          +--------------------+   |
       |   |   Tool Guidance   |          |     Subagents      |   |
       |   +-------------------+          +--------------------+   |
       |   +-------------------+          +--------------------+   |
       |   |      Skills       |          |      Scripts       |   |
       |   +-------------------+          +--------------------+   |
       |   +-------------------+          +--------------------+   |
       |   |      Plugins      |          |  Memory / Feedback |   |
       |   +-------------------+          +--------------------+   |
       +-----------------------------------------------------------+
                                     |
                                     v
                       +---------------------------+
                       |    Modelo LLM Congelado   |
                       +---------------------------+
```

### Los 8 Componentes del Arnés
1. **System Prompt (Identidad y Directivas Base):** Reglas ontológicas, estilo de comunicación y límites operativos fundamentales.
2. **Guardrails (Vallas de Seguridad):** Validadores sintácticos, filtros semánticos y reglas negativas (*Iron Laws*) que impiden acciones destructivas.
3. **Tool Guidance (Guía de Herramientas):** Metadatos, descripciones semánticas y ejemplos de cuándo y cómo invocar cada herramienta disponible.
4. **Subagents (Especialistas):** Perfiles secundarios aislados para delegar subtareas con contextos limpios y roles hiper-enfocados.
5. **Skills (Procedimientos Modulares):** Documentos `SKILL.md` que encapsulan patrones probados, heurísticas y metodologías ejecutables bajo demanda.
6. **Scripts (Herramientas Auxiliares Deterministas):** Programas ejecutables (Python, Bash, Node.js) que ejecutan transformaciones complejas sin gastar contexto ni alucinar cálculos.
7. **Plugins / Hooks (Middleware de Intercepción):** Puntos de intercepción en el ciclo de vida del agente (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) para auditar o reescribir flujos.
8. **Memory & Feedback (Memoria y Retroalimentación Continua):** Registros persistentes de experiencias pasadas, lecciones aprendidas y estados de sesión (`claude-mem`).

---

## 2. El Ciclo Recursivo: Propose – Probe – Compose

El núcleo metodológico de Harness² consiste en tratar la optimización del arnés como un problema de búsqueda evolutiva guiada por evidencia contrastiva, dividida en tres etapas cíclicas:

```
               +--------------------------------------+
               |               OBSERVAR               |
               | (Fallo en tarea, ineficiencia, etc.) |
               +--------------------------------------+
                                   |
                                   v
               +--------------------------------------+
               |             1. PROPOSE               |
               | - Formular hipótesis de mejora       |
               | - Diseñar mutación en arnés          |
               |   (Prompt, Skill, Script, Guardrail) |
               +--------------------------------------+
                                   |
                                   v
               +--------------------------------------+
               |              2. PROBE                |
               | - Ejecutar pruebas contrastivas      |
               | - Comparar Baseline vs Mutación      |
               | - Evaluar Tasa Éxito / Consumo Token |
               +--------------------------------------+
                                   |
                     +-------------+-------------+
                     |                           |
                 [PASA]                      [FALLA]
                     |                           |
                     v                           v
       +----------------------------+   +-------------------+
       |        3. COMPOSE          |   |  Refactorizar o   |
       | - Fusionar en arnés vivo   |   | Descartar Hipótesis|
       | - Registrar en Bitácora    |   +-------------------+
       | - Versionar en Git         |
       +----------------------------+
```

### Etapa 1: Propose (Formulación de Mutaciones)
Cuando un agente experimenta un fallo recurrente, un desvío de comportamiento o una ineficiencia en el consumo de tokens:
- **Análisis de Causa Raíz:** Se aísla cuál de los 8 componentes causó la deficiencia (ej. ¿falta de una regla en Guardrails? ¿descripción ambigua en `SKILL.md`? ¿ausencia de un script auxiliar determinista?).
- **Generación de Mutación:** Se redacta una modificación mínima y autocontenida (principio *Ponytail* / YAGNI).

### Etapa 2: Probe (Evaluación Contrastiva / TDD de Comportamiento)
Ninguna mutación se aprueba sin someterla al banco de pruebas:
- **Prueba Baseline (RED):** Se somete un subagente sin la mutación a un escenario de estrés (`pressure scenario`). Se documenta el modo exacto de fallo o racionalización tramposa.
- **Prueba con Mutación (GREEN):** Se repite exactamente el mismo escenario bajo las mismas semillas con la mutación activa.
- **Métricas Contrastivas Evaluadas:**
  1. *Success Rate (% de cumplimiento del criterio de aceptación).*
  2. *Token Efficiency (Consumo de tokens de entrada y salida).*
  3. *Step Latency (Número de llamadas a herramientas necesarias).*
  4. *Rule Compliance (Adhesión estricta a guardrails).*

### Etapa 3: Compose (Fusión y Refinamiento Acumulativo)
Si y sólo si la prueba contrastiva confirma una mejora neta sin efectos secundarios (*regresiones*):
- **Integración Atómica:** La mutación se incorpora al archivo definitivo (`SKILL.md`, `hooks.json`, o script en `tools/`).
- **Registro en la Bitácora de Lecciones:** Se documenta el hallazgo en `research/lessons_learned.md`.
- **Compromiso en Control de Versiones:** Se crea un commit en Git que garantiza trazabilidad y posibilidad de rollback instantáneo.

---

## 3. Adaptación al Hub de Antigravity (`c:\Users\cesar\Desktop\skill`)

En nuestro entorno, el ciclo Harness² se implementa mediante la combinación sinérgica de las herramientas existentes en el workspace:

| Rol Harness² | Implementación en Nuestro Workspace | Ubicación |
| :--- | :--- | :--- |
| **Generador de Mutaciones** | Agente principal guiado por `skills/writing-skills` | `skills/writing-skills/SKILL.md` |
| **Filtro de Calidad Sintáctico** | Validador automatizado `validate_skill.py` | `tools/validate_skill.py` |
| **Banco de Pruebas y Métricas** | Herramienta de benchmark `benchmark_skills.py` | `tools/benchmark_skills.py` |
| **Aislamiento de Pruebas** | Subagentes efímeros (`invoke_subagent`) y Worktrees | `tools/sandbox_runner.py` |
| **Memoria Evolutiva** | Integración nativa de `claude-mem` + Hooks de ciclo de vida | `~/.gemini/config/hooks.json` |
| **Persistencia Acumulativa** | Bitácora de Lecciones Aprendidas | `research/lessons_learned.md` |

---

## 4. Protocolo Operativo Paso a Paso para Nuevas Skills

Cuando se requiera crear una nueva skill para el catálogo:

1. **Definir el Escenario de Presión (RED):**
   - Redactar el prompt de prueba donde un agente estándar suele fallar, alucinar o tomar caminos sobre-complejos.
2. **Probar el Fallo Inicial:**
   - Registrar la racionalización o error típico en el baseline.
3. **Redactar el Borrador de `SKILL.md`:**
   - Frontmatter YAML estricto con `name` y `description: "Use when..."`.
   - Cero spoilers del flujo en la descripción para evitar que el agente salte la lectura del cuerpo.
   - Instrucciones claras, compactas y deterministas.
4. **Validación Automática:**
   ```powershell
   python tools/validate_skill.py skills/<nueva-skill>
   ```
5. **Auditoría de Desempeño y Tokens:**
   ```powershell
   python tools/benchmark_skills.py --skill skills/<nueva-skill>
   ```
6. **Composición y Versión:**
   - Si la validación y el benchmark son satisfactorios, registrar en el roadmap, sincronizar y hacer commit en Git.
