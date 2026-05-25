# 📊 Análisis de Selección de Modelo Predictivo: Regresión Lineal Ridge

Este documento detalla la justificación metodológica y técnica de por qué se ha seleccionado la **Regresión Lineal Ridge** como el modelo base para el sistema de predicción de ACWR (Acute:Chronic Workload Ratio) en el proyecto **SmartLoad**.

---

## 📈 Tabla Comparativa de Rendimiento (Set de Validación)

El set de prueba representa el **10% cronológico final** de la línea temporal de cada jugador, garantizando que el modelo sea evaluado en su capacidad de predecir el futuro real de los atletas.

| Algoritmo | RMSE (Root Mean Squared Error) | MAE (Mean Absolute Error) | $R^2$ (Coeficiente de Determinación) |
| :--- | :---: | :---: | :---: |
| **Ridge Linear Regression** *(Seleccionado)* | **1.4154** | 1.1094 | **0.1142** |
| **Random Forest Regressor** | 1.4282 | **1.0286** | 0.0981 |
| **Gradient Boosting Regressor** | 1.4600 | 1.1135 | 0.0575 |

---

## 🧠 Justificación de la Selección (¿Por qué Regresión Lineal?)

La decisión de avanzar con la **Regresión Lineal (con Regularización Ridge)** sobre modelos ensamblados más complejos (Random Forest y Gradient Boosting) se basa en cuatro pilares críticos:

### 1. Mayor Capacidad de Generalización (Evita el Overfitting)
Los modelos complejos como Gradient Boosting y Random Forest tienden a memorizar patrones muy específicos del historial de entrenamiento pasado (ruido). Al evaluar con un **split cronológico estricto** (el futuro de los jugadores), los modelos ensamblados sufrieron de sobreajuste (overfitting), resultando en un menor coeficiente de determinación ($R^2 = 0.0575$ para GBR y $0.0981$ para Random Forest). 
La **Regresión Ridge**, al aplicar una penalización L2 sobre los coeficientes grandes, simplifica la función de decisión y ofrece la mejor generalización en datos futuros ($R^2 = 0.1142$, y el menor RMSE de **1.4154**).

### 2. Interpretabilidad para el Staff Técnico y Preparadores Físicos
En el fútbol profesional, el preparador físico y el cuerpo médico no aceptarán una alerta de lesión proveniente de una "caja negra". Necesitan saber **el porqué**.
* La Regresión Lineal entrega coeficientes directos (pesos $\beta$) para cada variable.
* Permite explicar de forma clara: *"El jugador X tiene un ACWR proyectado de 1.6 debido a que su distancia en alta velocidad aumentó un 40% en los últimos 3 días, mientras que su carga crónica se mantuvo baja"*.

### 3. Facilidad para Simulaciones de Escenarios (What-If)
Uno de los objetivos principales de SmartLoad es permitir que el staff técnico simule entrenamientos futuros (ej. *"¿Qué pasa con el ACWR si mañana programamos un entrenamiento cardiovascular intenso?"*). 
Al ser un modelo lineal, la relación entrada-salida es directa y predecible. Esto hace que las simulaciones de simulación "What-If" en la aplicación interactiva sean inmediatas, estables y matemáticamente transparentes para el usuario final.

### 4. Estabilidad ante Cambios de Régimen
El rendimiento físico y las cargas de los futbolistas cambian drásticamente debido a viajes, partidos de copa o periodos de descanso. Los árboles de decisión (Random Forest / GBR) no pueden extrapolar bien fuera del rango de datos con el que fueron entrenados. La Regresión Lineal ofrece extrapolaciones mucho más estables y lógicas frente a cambios bruscos de calendario.

---

## 🛠️ Conclusión e Implementación
El modelo de Regresión Ridge ha sido serializado exitosamente en [models/best_acwr_model.joblib](file:///C:/Users/rafal_i75efg1/Documents/Master%20Big%20Data%20RM/Practicas/smartload/models/best_acwr_model.joblib) y se utilizará como motor predictivo para alimentar el componente de visualización interactivo (dashboard).
