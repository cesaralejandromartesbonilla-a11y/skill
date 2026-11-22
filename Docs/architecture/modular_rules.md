# Reglas de Arquitectura Modular y Desacoplamiento

> **Referencia:** Extraído y ampliado para prevención de código espagueti en agentes.

---

## 1. Reglas Cardinales

1. **Límite de Longitud por Archivo:** Ningún script debe exceder 250-300 líneas si mezcla responsabilidades.
2. **Separación de Capas:**
   - **Input:** Captura de eventos de usuario o entradas externas.
   - **State Machine / FSM:** Transiciones y reglas lógicas de estado.
   - **Kinematics / Física:** Ecuaciones de movimiento, integración y colisiones (`_physics_process`).
   - **Rendering / Audio:** Actualización de mallas, shaders, animaciones o sonido (`_process`).
3. **Comunicación por Señales:**
   - Dirección **Abajo $\to$ Arriba:** Exclusivamente mediante `signal` desacoplada.
   - Dirección **Arriba $\to$ Abajo:** Llamadas directas (`call` o método directo).
4. **Inversión de Dependencias:** El núcleo matemático o de reglas de negocio nunca debe importar APIs pesadas de motor (`bpy`, librerías I/O). Debe operar sobre contratos y modelos puros.
