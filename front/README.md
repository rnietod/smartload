# 🎨 SmartLoad — Visualización e Interfaz Interactiva (Frontend)

Esta carpeta albergará la interfaz de usuario interactiva y el panel de visualización desarrollado para el **cuerpo técnico y los preparadores físicos del club**. 

La interfaz traducirá las complejas predicciones de nuestro modelo en insights accionables en un clic, eliminando la necesidad de realizar consultas directas o interactuar con código.

---

## 🛠️ Stack Tecnológico Propuesto
* **Core**: **Streamlit** (La herramienta estándar de oro para aplicaciones interactivas de ciencia de datos veloces, elegantes y altamente responsivas en Python).
* **Gráficos**: **Plotly / Matplotlib** (Para renderizar curvas dinámicas interactivas de ACWR con bandas de color que demarquen las zonas de riesgo fisiológico).
* **Estilo**: CSS personalizado integrado en Streamlit para ofrecer una estética premium y minimalista (tema oscuro deportivo, fuentes modernas como *Inter* o *Outfit*, y bordes suaves de tipo *glassmorphism*).

---

## 📋 Arquitectura Diseñada para la Interfaz

La aplicación se dividirá en tres secciones funcionales clave:

### 1. 🚨 Team Alert Dashboard (Panel de Alertas del Plantel)
* **Objetivo**: Brindar una vista panorámica instantánea del estado de fatiga del equipo.
* **Componentes**:
  * Un contador de jugadores en zona de **Peligro (ACWR > 1.5)** y zona de **Subcarga (ACWR < 0.8)**.
  * Una tabla interactiva de atletas ordenados de mayor a menor riesgo de lesión, facilitando al cuerpo médico identificar a quién se debe dosificar hoy mismo.

### 2. 📈 Individual Athlete Tracker (Seguimiento del Jugador a 15 días)
* **Objetivo**: Analizar en detalle la proyección cronológica de un futbolista individual.
* **Componentes**:
  * Un selector desplegable para buscar a cualquier jugador del plantel.
  * Una ficha técnica con su perfil (altura, peso, edad, posición de juego).
  * Un gráfico de línea dinámico que proyecte su **ACWR de distancia a 15 días vista**.
  * **Bandas de Fondo Semafóricas**: El gráfico tendrá bandas de colores de fondo transparentes para clasificar visualmente el riesgo al instante:
    * 🟩 **Verde (0.8 - 1.3)**: Zona óptima.
    * 🟨 **Amarillo (1.3 - 1.5)**: Zona de precaución.
    * 🟥 **Rojo (> 1.5 o < 0.8)**: Zona de peligro / alerta.

### 3. 🧪 Simulador "What-If" (Planificación Dinámica del Entrenamiento)
* **Objetivo**: Permitir al cuerpo técnico probar sesiones de entrenamiento en tiempo real antes de programarlas en el calendario.
* **Componentes**:
  * Deslizadores interactivos (*sliders*) para configurar las métricas propuestas para el entrenamiento de mañana:
    * *Distancia Total Propuesta (metros)*
    * *Aceleraciones propuestas (esfuerzo count)*
    * *Distancia en alta velocidad propuesta (metros)*
  * **Predicción Instantánea**: Al ajustar los sliders, el modelo de Regresión Ridge recalculará el ACWR de forma inmediata y redibujará la rampa del gráfico, mostrando el impacto exacto que tendría la sesión programada sobre la fatiga del jugador en los próximos días.

---

## 🏃 Guía de Inicio (Próximamente)
Una vez iniciada la fase de desarrollo del front, los preparadores físicos podrán lanzar el panel interactivo de forma local mediante:
```bash
streamlit run front/app.py
```
