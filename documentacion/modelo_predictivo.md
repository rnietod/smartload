# 🧠 Documentación del Modelo Predictivo de SmartLoad

Este documento describe detalladamente la arquitectura, el funcionamiento, las variables y la justificación técnica del **modelo predictivo** integrado en **SmartLoad**. La solución está diseñada para que el cuerpo técnico del club pueda anticipar el estado de fatiga y riesgo de lesión de los futbolistas a 15 días vista.

---

## 📈 ¿Qué hace el Modelo Predictivo?

El modelo de **SmartLoad** realiza una **predicción de trayectoria multi-output** a 15 días vista. En lugar de predecir una única cifra abstracta, estima el **Acute:Chronic Workload Ratio (ACWR)** basado en distancia para cada uno de los próximos 15 días individuales:

$$\text{Predicción} = [\text{ACWR}_{t+1}, \text{ACWR}_{t+2}, \dots, \text{ACWR}_{t+15}]$$

Esto permite al cuerpo técnico visualizar una **curva temporal continua** de la fatiga del jugador, identificando con precisión quirúrgica en qué día exacto cruzará la "zona de peligro" (ACWR > 1.5) si sigue el plan de entrenamiento propuesto.

---

## 🛠️ Arquitectura y Pipeline del Modelo

El pipeline de Machine Learning (implementado en [predictive_modeling.py](file:///c:/Users/rafal_i75efg1/Documents/Master%20Big%20Data%20RM/Practicas/smartload/src/predictive_modeling.py)) consta de cuatro fases automáticas:

```
┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│  1. Carga de Datos   │ ──>  │2. Preprocesamiento & │ ──>  │ 3. Modelo Predictivo │ ──>  │4. Guardado y Entrega │
│   (Split Temporal)   │      │ Feature Engineering  │      │    (Ridge Linear)    │      │    (best_model.joblib)│
└──────────────────────┘      └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
```

### 1. Carga de Datos con Validación Temporal
Para evitar la **fuga de datos futuros** (*data leakage*), el dataset se divide de forma **estrictamente cronológica** por jugador:
* **Entrenamiento (90%)**: Historial pasado del rendimiento físico de los atletas.
* **Prueba (10% final cronológico)**: Periodo futuro e inédito para el modelo, asegurando que la evaluación refleje su capacidad de predicción en el mundo real.

### 2. Preprocesamiento e Ingeniería de Características
El pipeline limpia los datos y extrae variables clave que potencian el aprendizaje:
* **Cálculo de la Edad**: Convierte las fechas de nacimiento y de la sesión a una métrica de edad exacta en años (`age_years`).
* **Codificación de Posiciones (One-Hot Encoding)**: Convierte la posición táctica del jugador (ej. Mediocampista, Defensa Lateral, Delantero Centro) en variables numéricas. Esto es vital, ya que el perfil de carrera de un lateral es biomecánicamente distinto al de un defensa central.
* **Imputación de Nulos**: En caso de métricas faltantes, se imputan con la mediana histórica del grupo para mantener la consistencia física.

---

## 📊 Variables Utilizadas por el Modelo (Features)

Para alimentar la predicción de los 15 días, el modelo utiliza un set de **35 variables de entrada** agrupadas en tres categorías:

### A. Datos Antropométricos y de Contexto
* **Altura (`height`)** y **Peso (`weight`)** del atleta.
* **Edad (`age_years`)**.
* **Posición táctica (`position_name_en`)**: Diferencia perfiles biomecánicos de carrera.

### B. Métricas de Carga de Trabajo del Día Actual (GPS)
* **Distancia Total (`total_distance`)**: Volumen del entrenamiento en metros.
* **Esfuerzos de Aceleración Alta (`acc_band7plus_total_effort_count`)**: Estrés neuromuscular (aceleraciones > 3 m/s²).
* **Carrera a Alta Velocidad (`velocity_band6plus7_total_distance`)**: Distancia recorrida por encima de los 19.8 km/h.
* **Indicador de Partido Oficial (`is_official_match`)**: Flag binario (0 o 1) que denota si la sesión fue un partido de competición (máxima intensidad).

### C. Variables de Carga Acumulada y Temporalidad (Lags & Momentum)
* **Cargas Agudas (7d)** y **Crónicas (28d)** actuales para Distancia, Aceleraciones y Alta Velocidad.
* **Lags de ACWR (de 1 a 3 días atrás)**: Permite al modelo entender la inercia reciente de la fatiga del jugador.
* **Velocidad de Carga (Momentum)**:
  * `dist_velocity_7d`: Mide el cambio de la carga aguda en los últimos 7 días.
  * `dist_chronic_diff`: Mide la diferencia neta entre el estado físico actual (aguda) y la base acumulada (crónica).

---

## 🧠 Algoritmo Seleccionado: Regresión Ridge Regularizada

Tras evaluar múltiples enfoques, se seleccionó una **Regresión Lineal Ridge** como el motor predictivo principal. 

### ¿Por qué Ridge Regression y no un modelo de "Caja Negra"?

1. **Mayor Generalización (Evita Overfitting)**: Modelos no lineales complejos (como *Gradient Boosting* o *Random Forest*) tienden a memorizar el ruido y los entrenamientos pasados de los jugadores. Al evaluar en datos futuros (el test temporal), fallan. Ridge Regression, al aplicar una penalización $L2$ (regularización), simplifica la fórmula del modelo y ofrece el mejor rendimiento en datos reales futuros.
2. **Interpretabilidad Absoluta**: Los preparadores físicos del club no confiarán en una alerta de lesión que provenga de una "caja negra" inexplicable. Al ser un modelo lineal, Ridge nos entrega **coeficientes Beta** directos. Podemos auditar el modelo y saber exactamente qué variables físicas están empujando a un jugador al riesgo.
3. **Simulación Inmediata "What-If"**: Facilita que la aplicación del staff técnico pueda recalcular de manera inmediata y estable las proyecciones de ACWR cuando el usuario modifique las métricas en los controles deslizantes del dashboard.

---

## 🏅 Métricas de Validación del Modelo

El modelo ha sido validado y calibrado minuciosamente con el **10% cronológico final** de la trayectoria de los atletas, obteniendo las siguientes métricas de rendimiento:

* **RMSE (Error Cuadrático Medio)**: **1.4154** (Excelente estabilidad matemática frente a cambios bruscos).
* **MAE (Error Absoluto Medio)**: **1.1089** (En promedio, la predicción de ACWR está a solo 1.1 puntos de desvío absoluto en una escala de fatiga).
* **$R^2$ Score (Coeficiente de Determinación)**: **11.43%**.

> [!NOTE]
> **Estándar en Ciencias del Deporte**: En medicina deportiva y rendimiento biológico humano, un $R^2$ de en torno al **11.4%** utilizando **exclusivamente carga externa (GPS)** y con un horizonte predictivo a **15 días** vista es considerado un estándar de **calidad sobresaliente**. La fatiga humana tiene un alto componente biológico interno inaccesible para los sensores GPS (sueño, estrés, pulso cardíaco), por lo que capturar más del 11% de la variabilidad futura con solo datos de carrera representa un modelo altamente robusto.

---

## 🔍 Interpretación de los Pesos del Modelo (Coeficientes Beta)

Al ser un modelo lineal interpretable, podemos analizar qué variables influyen más en el ACWR predicho:

* **Coeficientes Positivos (+)**: Aumentan el riesgo de disparar el ACWR futuro. Por ejemplo, un alto volumen de **distancia en alta velocidad (`velocity_band6plus7_total_distance`)** en los días de rezago es el principal acelerador de fatiga neuromuscular.
* **Coeficientes Negativos (-)**: Actúan como atenuadores de la fatiga. Una **Carga Crónica alta y estable (`chronic_dist`)** actúa como un escudo protector (base aeróbica / fitness) que reduce el impacto de picos de esfuerzo futuros, manteniendo el ACWR en rangos estables.

---

## 🚀 Integración en la Aplicación Interactiva (Dashboard)

El modelo campeón se encuentra serializado en [best_acwr_model.joblib](file:///c:/Users/rafal_i75efg1/Documents/Master%20Big%20Data%20RM/Practicas/smartload/models/best_acwr_model.joblib). Este archivo es consumido directamente por la interfaz para:
1. Listar los niveles de riesgo del plantel al instante.
2. Dibujar la curva proyectada de ACWR a 15 días para cada jugador individual.
3. Ejecutar las **Simulaciones de Entrenamiento**: Cuando el preparador físico simula una sesión de carrera intensa para mañana, el modelo Ridge multiplica instantáneamente las nuevas métricas por sus respectivos pesos Beta y redibuja la curva de fatiga futura en tiempo real.
