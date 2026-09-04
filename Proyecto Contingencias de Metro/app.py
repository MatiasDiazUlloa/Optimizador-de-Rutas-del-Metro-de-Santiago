import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from main import MetroRed, normalizar

app = FastAPI(title="Sistema Metro de Santiago")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

metro = MetroRed()
metro.cargar_datos()


@app.get("/", response_class=HTMLResponse)
async def home():
    with open(os.path.join(BASE_DIR, "templates", "index.html"), "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/route")
async def calcular_ruta(data: dict):
    origen = data.get("origen", "")
    destino = data.get("destino", "")
    criterio = int(data.get("criterio", 1))
    resultado = metro.calcular_ruta(origen, destino, criterio)
    return {"resultado": resultado}


@app.post("/api/contingency/station")
async def cerrar_estacion(data: dict):
    nombre = data.get("nombre", "")
    est_real = next((e for e in metro.estaciones_fisicas if normalizar(e) == normalizar(nombre)), None)
    if est_real:
        metro.fallas_estaciones.add(est_real)
        return {"success": True, "mensaje": f"[{est_real}] inhabilitada"}
    return {"success": False, "mensaje": "Error: Estacion no encontrada."}


@app.post("/api/contingency/tramo")
async def cerrar_tramo(data: dict):
    e1 = data.get("e1", "")
    e2 = data.get("e2", "")
    e1_real = next((e for e in metro.estaciones_fisicas if normalizar(e) == normalizar(e1)), None)
    e2_real = next((e for e in metro.estaciones_fisicas if normalizar(e) == normalizar(e2)), None)

    if not e1_real or not e2_real:
        return {"success": False, "mensaje": "Error: Una o ambas estaciones no existen en la red."}

    ruta = metro._buscar_segmento_continuo(e1_real, e2_real)
    if ruta:
        for i in range(len(ruta) - 1):
            metro.fallas_tramos.add(frozenset({ruta[i], ruta[i + 1]}))
        trayecto = " - ".join(f"{n[1]} ({n[0]})" for n in ruta)
        return {"success": True, "mensaje": "Tramo bloqueado exitosamente.", "trayecto": trayecto}
    return {"success": False, "mensaje": f"Error: No existe una via continua directa entre [{e1}] and [{e2}]."}


@app.get("/api/diagnostico")
async def diagnostico():
    return {"resultado": metro.evaluar_conectividad()}


@app.post("/api/reset")
async def resetear():
    global metro
    metro = MetroRed()
    metro.cargar_datos()
    return {"success": True, "mensaje": "Sistema reiniciado correctamente."}


@app.get("/api/estaciones")
async def obtener_estaciones():
    return {"estaciones": sorted(list(metro.estaciones_fisicas))}


@app.get("/api/state")
async def obtener_estado():
    return {
        "fallas_estaciones": sorted(list(metro.fallas_estaciones)),
        "fallas_tramos": sorted(list(metro.fallas_tramos)),
        "total_estaciones": len(metro.estaciones_fisicas)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)