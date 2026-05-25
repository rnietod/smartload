# ⚽ SmartLoad — Predicción de Carga de Trabajo y Ratio ACWR para Futbolistas

SmartLoad es una herramienta de análisis predictivo avanzada desarrollada para el **Departamento de Datos del Club** (preparación física y rendimiento de fútbol). Utiliza modelos de Machine Learning para predecir el **Acute vs Chronic Workload Ratio (ACWR)** a 15 días vista para prevenir lesiones y optimizar el rendimiento del plantel.

---

## 🚀 Arquitectura y Componentes del Sistema

El flujo del proyecto consta de tres fases fundamentales:

```
[Raw Data: CSV] 
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Data Engineering Pipeline (data_engineering.py)      │
├─────────────────────────────────────────────────────────┤
│ - Limpieza y formateo de datos.                         │
│ - Agregación de sesiones a nivel diario por jugador.    │
│ - Reindexación temporal (relleno de días de descanso).   │
│ - Cálculo de cargas rolling (Aguda 7d y Crónica 28d).   │
│ - Creación del target predictivo a 15 días vista.       │
│ - División train/test cronológica (10% test).           │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ├──────────────────────────────┐
                           ▼                              ▼
                 [processed_train.csv]          [processed_test.csv]
                           │                              │
                           └──────────────┬───────────────┘
                                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Predictive Modeling & Evaluation (predictive_ml.py)  │
├─────────────────────────────────────────────────────────┤
│ - Carga y procesamiento de splits temporales.           │
│ - Codificación categórica de la posición del jugador.   │
│ - Entrenamiento de modelos: Ridge, Random Forest, GBR.  │
│ - Validación rigurosa (RMSE, MAE, R²).                  │
│ - Exportación del modelo campeón a joblib.              │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
              [models/best_acwr_model.joblib]
```

---

## 📊 Conceptos Clave — ¿Qué es el ACWR?

El **Acute:Chronic Workload Ratio** compara el nivel de fatiga a corto plazo con el nivel de fitness acumulado a largo plazo:
- **Carga Aguda (Acute Load):** Suma o promedio de carga de trabajo (distancia recorrida, aceleraciones, etc.) de los últimos **7 días**.
- **Carga Crónica (Chronic Load):** Promedio de carga de trabajo de los últimos **28 días** (4 semanas).

$$\text{ACWR} = \frac{\text{Carga Aguda (7 días)}}{\text{Carga Crónica (28 días)}}$$

### 🚦 Zonas de Riesgo de Lesión:
- **< 0.8:** Subentrenamiento (riesgo de desentrenamiento).
- **0.8 a 1.3:** **Zona óptima** (mayor adaptabilidad, bajo riesgo de lesiones).
- **1.3 a 1.5:** Zona de precaución.
- **> 1.5:** **Zona de peligro** (elevado riesgo de lesión por sobreesfuerzo).

---

## 📁 Estructura del Directorio

```
smartload/
├── .git/                      # Repositorio Git vinculado al remoto
├── .gitignore                 # Exclusiones de data y archivos de entorno
├── data/                      # Almacén de datasets (excluido en git)
│   ├── data_acute_vs_chronic.csv  # Dataset en bruto (3,903 registros)
│   ├── processed_full.csv     # Dataset limpio continuo con rolling features
│   ├── processed_train.csv    # Set de entrenamiento (90% cronológico)
│   └── processed_test.csv     # Set de prueba (10% cronológico final)
├── models/                    # Modelos entrenados y serializados
│   └── best_acwr_model.joblib # Modelo campeón guardado para el dashboard
├── data_engineering.py        # Pipeline de ingeniería de datos y features
├── predictive_modeling.py     # Script de modelado ML y evaluación
├── requirements.txt           # Dependencias requeridas del proyecto
├── PROJECT_CONTEXT.md         # Contexto y requerimientos del negocio
└── README.md                  # Esta guía del usuario y arquitectura
```

---

## 🛠️ Instalación y Configuración

1. **Clonar el Repositorio:**
   ```bash
   git clone https://github.com/rnietod/smartload.git
   cd smartload
   ```

2. **Instalar Dependencias:**
   Se recomienda usar un entorno virtual de Python (>= 3.9):
   ```bash
   pip install -r requirements.txt
   ```

---

## 🏃 Cómo Ejecutar las Fases

### Fase 1: Ingeniería de Datos
Este paso limpia el CSV de Databricks, agrega sesiones dobles a nivel diario por jugador, reconstruye el calendario diario ininterrumpido (rellenando días de descanso con 0 para evitar distorsiones de rolling windows), computa el ACWR real de entrenamiento y genera los sets de entrenamiento/prueba chronológicos:
```bash
python data_engineering.py
```
*Salida:* `processed_train.csv`, `processed_test.csv` y `processed_full.csv` guardados en el directorio `data/`.

### Fase 2: Entrenamiento Predictivo y Evaluación
Carga la data estructurada de la fase anterior, entrena tres algoritmos alternativos (Regresión Ridge, Random Forest Regressor y Gradient Boosting Regressor) prediciendo el ACWR a 15 días vista, y evalúa el desempeño en el set de prueba usando las métricas exigidas del negocio (**RMSE**, **MAE** y **R²**):
```bash
python predictive_modeling.py
```
*Salida:* Reporte de métricas por consola, desglose de las variables más importantes e importación del modelo óptimo guardado en `models/best_acwr_model.joblib`.

---

## 📄 Licencia
Este proyecto es de código abierto y está licenciado bajo la **Apache License, Version 2.0**.
