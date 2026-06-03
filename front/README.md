# 🎨 SmartLoad — Panel de Control e Interfaz Interactiva (Frontend)

Este directorio contiene la interfaz de usuario interactiva para el cuerpo técnico y preparadores físicos del club. Desarrollada con tecnologías web modernas, permite visualizar en tiempo real las alertas de fatiga de la plantilla, el historial de carga de trabajo, y realizar simulaciones mediante el modelo predictivo de Machine Learning.

---

## 🚀 Tecnologías Utilizadas

- **React 19** & **Vite**: Para un desarrollo rápido, modular y con recarga rápida en tiempo real (HMR).
- **HeroUI (v2)**: Biblioteca de componentes de UI moderna, accesible y estilizada.
- **Tailwind CSS**: Framework de diseño y diseño visual premium con tokens personalizados.
- **Recharts**: Para la renderización fluida e interactiva de gráficos cronológicos de ACWR y proyecciones de fatiga.
- **Lucide React**: Set de iconos vectoriales modernos y estilizados.
- **Framer Motion**: Para micro-animaciones fluidas y transiciones interactivas.

---

## 📋 Características Principales

### 1. 🚨 Roster de Selección Élite (Roster Section)
- Tarjetas individuales de los jugadores (leyendas del Real Madrid con apodos interactivos).
- Visualización compacta del ACWR actual con minigráficos (*sparklines*) de tendencia de los últimos 7 días.
- Filtro rápido de ordenación según el riesgo de lesión o fatiga (de mayor a menor).
- Alertas de peligro visuales según la zona fisiológica del ACWR.

### 2. 📊 Bento Grid de Monitoreo Individual
- **Ficha Técnica del Atleta (BioCard)**: Información antropométrica (altura, peso, edad en años decimales, posición).
- **Visualizador Digital de ACWR**: Estado actual con color codificado según zonas clínicas (Óptimo, Precaución, Peligro, Subcarga).
- **Gráfico de Fatiga y Proyecciones IA (FatigueChart)**:
  - Muestra los 14 días previos de datos reales acumulados.
  - Muestra la proyección fisiológica exacta de los siguientes 15 días.
  - Superpone la **predicción multivariable del modelo de Inteligencia Artificial (Ridge Regression)** a 15 días vista.
  - Bandas de color semafóricas que marcan las zonas críticas de fatiga.

### 3. 🧪 Planificador de Escenarios "What-If"
- Permite al preparador físico simular una planificación a 7 días.
- Esquema simplificado de microciclo: `-2 (Ligera)`, `-1 (Descanso)`, `Partido`, `+1 (Normal)`, `+2 (Alta Intensidad)`, `+3 (Ligera)` y `Partido 2`.
- Al alterar el plan de cualquiera de los días, la aplicación envía los datos al backend de FastAPI, ejecuta el modelo de Ridge en tiempo real y actualiza dinámicamente la rampa proyectada en el gráfico.

### 4. 📂 Subida Demostrativa de Archivos CSV
- Modal de subida interactivo (Drag & Drop) para que el preparador físico cargue nuevos datasets de telemetría GPS de forma visual.

---

## 🏃 Cómo Ejecutar el Frontend Localmente

1. Asegúrate de tener instalado **Node.js** (versión 18 o superior recomendada).
2. Entra en el directorio del frontend e instala las dependencias:
   ```bash
   cd front
   npm install
   ```
3. Inicia el servidor de desarrollo de Vite:
   ```bash
   npm run dev
   ```
4. El servidor se ejecutará por defecto en `http://localhost:5173`. Las llamadas a `/api` se redirigen automáticamente al backend (FastAPI en `http://127.0.0.1:8000`) gracias al proxy configurado en `vite.config.js`.

> [!TIP]
> Puedes utilizar el script lanzador unificado `start.bat` situado en la raíz del proyecto para iniciar tanto el Backend FastAPI como el Frontend Vite de manera automática con un solo doble clic.
