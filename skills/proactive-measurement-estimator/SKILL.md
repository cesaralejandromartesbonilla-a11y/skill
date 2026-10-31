---
name: proactive-measurement-estimator
description: Protocolo de ingeniería y herramientas de cálculo dimensional, estimación de materiales (takeoff), despiece y aclaración proactiva de requerimientos. Úsalo SIEMPRE que el usuario plantee problemas de medición, construcción, cálculo de piezas/tablas/paneles, o preguntas amplias donde factores como vanos (ventanas/puertas), traslapes, orientación de corte, mermas, inclinaciones o tolerancias afecten drásticamente el resultado final.
---

# Proactive Measurement & Estimator

Cuando un usuario solicita un cálculo dimensional, estimación de materiales (madera, perfiles, drywall, tubería, recubrimientos) o despiece:
> **REGLA FUNDAMENTAL:** Un cálculo matemático exacto sobre premisas incompletas es un error de ingeniería. Nunca entregues una cifra cerrada superficial sin antes conceptualizar el problema, interrogar activamente sobre factores de obra y presentar el rango de escenarios reales.

---

## 1. Protocolo de Aclaración Previa Obligatoria

Antes de emitir el reporte final de despiece o compra, debes plantear o verificar de forma proactiva estos **6 factores críticos de obra**:

| Factor Crítico | Pregunta al Usuario / Variable Técnica | Impacto en el Resultado |
| :--- | :--- | :--- |
| **1. Vanos y Aberturas** | ¿Existen ventanas, puertas, ductos, columnas o nichos en las superficies a cubrir? | Reduce el área neta pero puede aumentar la merma por cortes perimetrales. |
| **2. Traslape / Unión** | ¿Las tablas van a tope, machihembradas (*tongue-and-groove*) o traslapadas (*shiplap*)? ¿Cuál es el ancho útil cubriente? | Si una tabla mide 38.3 cm de ancho pero tiene 1.5 cm de traslape, el ancho efectivo es 36.8 cm, exigiendo más tablas. |
| **3. Orientación y Cortes** | ¿Se instalarán vertical u horizontalmente? ¿Se permite unir retales sobrantes (*offcuts*) o cada tramo debe ser continuo? | La orientación vertical elimina juntas visibles pero si la pared supera el largo de la tabla se genera desperdicio o empalmes. |
| **4. Encuentros y Esquinas** | ¿El encuentro entre paredes es a escuadra ($90^\circ$), inglete ($45^\circ$) o a tope? ¿Las paredes tienen desplome o inclinación? | Las paredes fuera de plomo exigen cortes en cuña y mayor sobremedida. |
| **5. Margen de Merma (Waste Factor)** | ¿Qué porcentaje de seguridad o merma aplicamos según la complejidad? | Estándar de construcción: **5%** (cortes rectos uniformes), **10%** (con vanos y esquinas), **15%** (instalación diagonal o muros irregulares). |
| **6. Fijaciones y Base** | ¿Sobre qué estructura se fijan (rastreles/listones, perfiles omega)? ¿Requiere espacio perimetral de dilatación? | Determina si la primera y última tabla deben recortarse a eje. |

---

## 2. Marco Matemático de Despiece Exacto

### Conversión Estricta de Unidades
Utiliza constantes físicas y factores de conversión exactos:
$$1\text{ in} = 0.0254\text{ m} = 2.54\text{ cm}$$
$$1\text{ ft} = 12\text{ in} = 0.3048\text{ m}$$

### Ejemplo Paradigmático: Despiece de Paredes con Tablas
**Enunciado típico:** Pared 1 de $98''$ de ancho, Pared 2 de $45''$ de ancho, ambas con altura de $114''$. Tablas de $38.3\text{ cm} \times 2.90\text{ m}$.

#### A. Conversión Dimensional
- **Altura Paredes:** $114\text{ in} \times 0.0254 = 2.8956\text{ m}$.
  - Largo tabla: $2.90\text{ m}$.
  - Sobrante longitudinal por tabla vertical: $2.90\text{ m} - 2.8956\text{ m} = 0.0044\text{ m} = 4.4\text{ mm}$ (ajuste casi exacto, cero retal útil).
- **Ancho Pared 1:** $98\text{ in} \times 0.0254 = 2.4892\text{ m} = 248.92\text{ cm}$.
- **Ancho Pared 2:** $45\text{ in} \times 0.0254 = 1.1430\text{ m} = 114.30\text{ cm}$.
- **Ancho Total Acumulado:** $143\text{ in} \times 0.0254 = 3.6322\text{ m} = 363.22\text{ cm}$.

#### B. Análisis de Escenarios Reales
1. **Escenario Teórico Geométrico (A Tope, Sin Traslape, Sin Vanos, Paredes Continuas):**
   - Columnas necesarias: $363.22\text{ cm} / 38.3\text{ cm} = 9.48 \rightarrow \mathbf{10\text{ tablas}}$.
   - *Fallo de este cálculo:* Asume que el sobrante de $0.52$ de tabla de la pared 1 puede doblarse mágicamente hacia la pared 2 sin desperdicio en la esquina.
2. **Escenario Real de Montaje Pared por Pared (Sin Traslape):**
   - Pared 1 ($248.92\text{ cm}$): $248.92 / 38.3 = 6.50 \rightarrow \mathbf{7\text{ tablas}}$ (6 enteras + 1 cortada a $19.1\text{ cm}$).
   - Pared 2 ($114.30\text{ cm}$): $114.30 / 38.3 = 2.98 \rightarrow \mathbf{3\text{ tablas}}$ (2 enteras + 1 cortada a $37.7\text{ cm}$).
   - Si el sobrante longitudinal de $19.2\text{ cm}$ de la tabla de la Pared 1 no es reutilizable para cubrir el faltante de $37.7\text{ cm}$ de la Pared 2: Total = $7 + 3 = \mathbf{10\text{ tablas}}$ si no hay merma por rotura.
3. **Escenario con Traslape (Machihembrado de 1.5 cm útil):**
   - Ancho cubriente útil = $38.3 - 1.5 = 36.8\text{ cm}$.
   - Pared 1: $248.92 / 36.8 = 6.76 \rightarrow \mathbf{7\text{ tablas}}$.
   - Pared 2: $114.30 / 36.8 = 3.11 \rightarrow \mathbf{4\text{ tablas}}$.
   - Total con traslape = $7 + 4 = \mathbf{11\text{ tablas}}$ (más 1 tabla adicional de reserva por merma = **12 tablas recomendadas de compra**).

---

## 3. Plantilla de Respuesta al Usuario

Al responder a cualquier problema de este tipo, estructura siempre tu entrega en 3 secciones:

1. **Conceptualización y Supuestos Explícitos:** Declara las unidades convertidas y la orientación considerada.
2. **Preguntas de Validación de Obra:** Las 3 a 5 preguntas clave (vanos, traslape, tolerancia de esquinas, porcentaje de merma).
3. **Matriz de Escenarios (Teórico vs Real de Obra vs Compra Recomendada):** Brinda el número mínimo matemático y la recomendación profesional con margen de seguridad.
