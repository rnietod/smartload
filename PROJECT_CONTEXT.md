# 📋 PROJECT CONTEXT — Predicción del Ratio ACWR (Acute vs Chronic Workload Ratio)

> **Última actualización:** Mayo 2026  
> **Licencia:** Apache License, Version 2.0

---

## 1. Información General

| Campo            | Detalle                                                                 |
|------------------|-------------------------------------------------------------------------|
| **Proyecto**     | Predicción del Ratio Acute vs Chronic Workload para Jugadores           |
| **Cliente**      | Departamento de Data del Club (análisis avanzado de preparación física) |
| **Contratista**  | Grupo A                                                                 |
| **Fecha Inicio** | Marzo 2026                                                              |
| **Licencia**     | Apache License, Version 2.0                                             |

---

## 2. Contexto y Objetivos del Negocio

El Departamento de Datos del Club ha recopilado datos detallados de **carga de trabajo y rendimiento** durante las últimas dos temporadas. Aunque el almacenamiento es correcto, el cuerpo técnico y los preparadores físicos necesitan una herramienta interactiva que traduzca estos datos en **información accionable** sin necesidad de escribir código ni realizar consultas directas a bases de datos.

### 🎯 Objetivos Clave

1. Diseñar y construir una **herramienta de predicción y visualización del ACWR** para atletas de fútbol.
2. Utilizar el ACWR como **indicador clave** para evaluar el riesgo de lesiones y optimizar el rendimiento.
3. Permitir **simulaciones de escenarios (What-If)** basándose en el tipo de entrenamiento propuesto.

---

## 3. Planteamiento del Problema (Preguntas de Negocio)

La solución debe responder de forma autónoma a las siguientes cuestiones del staff técnico:

- ❓ **¿Cuál será el ACWR de los atletas si se realiza un entrenamiento de alta intensidad mañana?**
- ❓ **¿Qué atletas son más propensos a registrar un ACWR elevado** según su historial de entrenamientos y lesiones previas?

> **Problema actual:** La planificación se realiza basándose únicamente en la experiencia y en valores de métricas de los últimos días, **sin una perspectiva predictiva automatizada**.

---

## 4. Alcance Técnico de la Solución

### 4.1. Datos de Entrada

| Campo            | Detalle                                     |
|------------------|---------------------------------------------|
| **Origen**       | Espacio de trabajo compartido en Databricks |
| **Formatos**     | CSV / JSON                                  |

**Entidades incluidas:**
- Historial de entrenamientos y partidos (intensidad, duración, tipo de ejercicio, etc.)
- Métricas de carga de trabajo y fatiga de los atletas

---

### 4.2. Pipeline de Datos y Modelado

```
[Raw Data] ──► [Limpieza & Transformación] ──► [Feature Engineering] ──► [Modelo ML] ──► [Predicción ACWR]
```

| Fase                        | Descripción                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| **Preparación de Datos**    | Limpieza, transformación y preparación de los datos en bruto                |
| **Desarrollo del Modelo**   | Construcción de un modelo ML para predecir el ACWR; exploración de diversos algoritmos |
| **Validación**              | Evaluación con métricas de regresión: **RMSE**, **MAE** y **R²**            |

---

### 4.3. Componente de Visualización

Desarrollo de una **aplicación interactiva** que permita al equipo técnico:

- ✅ Seleccionar el **tipo de entrenamiento propuesto** (ej. fuerza, cardiovascular, etc.) para los próximos días.
- ✅ Visualizar de forma clara la **predicción del ACWR a 15 días vista** para cada atleta individual.

---

## 5. Entregables Obligatorios

| # | Entregable                    | Descripción                                                                                              |
|---|-------------------------------|----------------------------------------------------------------------------------------------------------|
| 1 | **Código del Pipeline y Modelo** | Notebooks o repositorios de Databricks con la preparación de datos y el desarrollo del modelo          |
| 2 | **Aplicación Interactiva**       | Aplicación desplegable y funcional para la interacción del usuario final                               |
| 3 | **Documentación Técnica**        | Documento con arquitectura de la solución, modelo de datos, metodología y guía de usuario              |

---

## 6. Conceptos Clave — Definición del ACWR

El **Acute:Chronic Workload Ratio (ACWR)** es un indicador de rendimiento y riesgo de lesión que compara:

- **Carga Aguda (Acute Load):** Carga de trabajo de los últimos **7 días** (fatiga a corto plazo).
- **Carga Crónica (Chronic Load):** Promedio de carga de trabajo de las últimas **4 semanas** (fitness a largo plazo).

```
ACWR = Carga Aguda (7 días) / Carga Crónica (28 días)
```

| Rango ACWR   | Interpretación                                |
|--------------|-----------------------------------------------|
| < 0.8        | Subcarga — posible desentrenamiento           |
| 0.8 – 1.3   | ✅ Zona óptima — bajo riesgo de lesión        |
| 1.3 – 1.5   | ⚠️ Zona de precaución                         |
| > 1.5        | 🔴 Alto riesgo de lesión                      |

---

## 7. Stack Tecnológico (Propuesto)

| Capa              | Tecnología                                         |
|-------------------|----------------------------------------------------|
| **Datos**         | Databricks, Delta Lake, CSV/JSON                   |
| **Procesamiento** | PySpark / Pandas                                   |
| **Modelado**      | Scikit-learn, MLflow (tracking de experimentos)    |
| **Visualización** | Streamlit / Dash / Databricks Apps                 |
| **Versioning**    | Git + Databricks Repos                             |

---

## 8. Notas Adicionales para el Agente

- Este documento actúa como **fuente de verdad** del proyecto. Consultar siempre antes de implementar cualquier componente.
- El foco del usuario final es **no técnico**: la interfaz debe ser intuitiva y sin jerga de programación.
- Priorizar la **interpretabilidad** del modelo sobre la complejidad (el staff técnico debe entender por qué un jugador tiene ACWR elevado).
- Los datos de las **dos últimas temporadas** son la fuente principal de entrenamiento.
- El horizonte de predicción principal es **15 días**.
