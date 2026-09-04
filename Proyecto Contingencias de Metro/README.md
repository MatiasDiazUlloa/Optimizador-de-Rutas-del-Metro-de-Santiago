# Sistema Metro de Santiago - Proyecto Contingencias

Sistema de gestión de red de metro con interfaz web que calcula rutas óptimas y simula contingencias (fallas).

## Estructura del proyecto

```
Proyecto Contingencias de Metro/
├── app.py                   # Servidor web (FastAPI)
├── main.py                  # Lógica del sistema metro
├── estaciones.txt           # Lista de estaciones de la red
├── vias.txt                 # Definición de vías
├── README.md                # Este archivo
├── .vscode/
│   └── launch.json          # Configuración de ejecución para VS Code
├── templates/
│   └── index.html           # Interfaz web principal
└── static/
    ├── style.css            # Estilos de la interfaz
    └── app.js               # Lógica del frontend
```

## Cómo ejecutar

### Interfaz web (recomendado)
```bash
cd Proyecto Contingencias de Metro
python app.py
```
Luego abrir en el navegador: **http://localhost:8000**

### Modo consola (tradicional)
```bash
cd Proyecto Contingencias de Metro
python main.py
```

### Desde VS Code
- Para la interfaz web: abrir `app.py` y presionar `F5`
- Para modo consola: abrir `main.py` y presionar `F5`

## Funcionalidades

### 🗺️ Ruta Óptima (P1)
- **Criterio 1:** Minimizar transbordos
- **Criterio 2:** Minimizar tiempo
- **Criterio 3:** Ambos criterios simultáneamente

### ⚠️ Contingencia (P2)
- **Cerrar Estación:** Los trenes pasan de largo, sin transbordos interlínea
- **Cerrar Tramo:** Bloquear un segmento continuo entre dos estaciones de la misma línea

### 📊 Estado de Red
- Diagnóstico de conectividad con componentes aislados
- Visualización de estaciones cerradas y tramos bloqueados

### 🔄 Reiniciar
- Restaura el sistema al estado inicial (sin fallas)

## Algoritmos utilizados

- **Dijkstra con pesos duales** para cálculo de rutas óptimas
- **BFS (Breadth-First Search)** para búsqueda de segmentos continuos y análisis de conectividad