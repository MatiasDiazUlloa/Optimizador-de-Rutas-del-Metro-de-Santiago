import heapq
from collections import deque
import sys
import os

TIEMPO_TRANSBORDO = 4
TIEMPO_NUEVA_LINEA = 6

def normalizar(texto):
    if not texto:
        return ""
    reemplazos = (
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("ñ", "n"), ("ü", "u")
    )
    texto = texto.lower()
    for a, b in reemplazos:
        texto = texto.replace(a, b)
    return texto


class MetroRed:
    """Sistema de gestión de red de metro con rutas óptimas y contingencias."""

    def __init__(self):
        self.grafo = {}
        self.estaciones_fisicas = set()
        self.fallas_estaciones = set()
        self.fallas_tramos = set()

    def agregar_arista(self, u, v, w_t, w_c):
        if u not in self.grafo:
            self.grafo[u] = []
        if v not in self.grafo:
            self.grafo[v] = []
        self.grafo[u].append((v, w_t, w_c))
        self.grafo[v].append((u, w_t, w_c))

    def cargar_datos(self):
        """Carga estaciones y vías desde archivos de texto en la misma carpeta del script."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        est_path = os.path.join(base_dir, 'estaciones.txt')
        vias_path = os.path.join(base_dir, 'vias.txt')

        if not os.path.exists(est_path) or not os.path.exists(vias_path):
            print("Error: No se encontraron los archivos estaciones.txt o vias.txt")
            sys.exit(1)

        try:
            with open(est_path, 'r', encoding='utf-8') as file_est:
                for linea in file_est:
                    estacion = linea.strip()
                    if estacion:
                        self.estaciones_fisicas.add(estacion)

            estaciones_por_linea = {}

            with open(vias_path, 'r', encoding='utf-8') as file_vias:
                for linea_texto in file_vias:
                    linea_texto = linea_texto.strip()
                    if not linea_texto:
                        continue

                    datos = linea_texto.split(',')
                    if len(datos) != 5:
                        continue

                    l_orig, est_orig_raw, l_dest, est_dest_raw, tiempo = [d.strip() for d in datos]

                    est_orig = next((e for e in self.estaciones_fisicas if normalizar(e) == normalizar(est_orig_raw)), None)
                    est_dest = next((e for e in self.estaciones_fisicas if normalizar(e) == normalizar(est_dest_raw)), None)

                    if not est_orig or not est_dest:
                        continue

                    nodo_u = (l_orig, est_orig)
                    nodo_v = (l_dest, est_dest)

                    self.agregar_arista(nodo_u, nodo_v, int(tiempo), 0)

                    if est_orig not in estaciones_por_linea:
                        estaciones_por_linea[est_orig] = set()
                    if est_dest not in estaciones_por_linea:
                        estaciones_por_linea[est_dest] = set()
                    estaciones_por_linea[est_orig].add(l_orig)
                    estaciones_por_linea[est_dest].add(l_dest)

            self._agregar_transbordos(estaciones_por_linea)

            print("Base de datos cargada sin problemas.\n")

        except Exception as e:
            print(f"Error carga de archivos: {e}")
            sys.exit(1)

    def _agregar_transbordos(self, estaciones_por_linea):
        """Agrega aristas de transbordo entre estaciones compartidas por múltiples líneas."""
        for estacion, lineas in estaciones_por_linea.items():
            lineas = list(lineas)
            for i in range(len(lineas)):
                for j in range(i + 1, len(lineas)):
                    nodo_a = (lineas[i], estacion)
                    nodo_b = (lineas[j], estacion)
                    self.agregar_arista(nodo_a, nodo_b, TIEMPO_NUEVA_LINEA, 1)

    def calcular_ruta(self, origen_ingresado, destino_ingresado, criterio):
        """Calcula la ruta óptima entre dos estaciones usando Dijkstra con pesos duales.

        Args:
            origen_ingresado: Nombre de la estación de origen.
            destino_ingresado: Nombre de la estación de destino.
            criterio: 1 = transbordos, 2 = tiempo, 3 = ambos.
        """
        origen_fisico = next((e for e in self.estaciones_fisicas if normalizar(e) == normalizar(origen_ingresado)), None)
        destino_fisico = next((e for e in self.estaciones_fisicas if normalizar(e) == normalizar(destino_ingresado)), None)

        if not origen_fisico or not destino_fisico:
            return "Error: Estacion no existe. Revisa como la escribiste."

        if origen_fisico in self.fallas_estaciones or destino_fisico in self.fallas_estaciones:
            return "Error: Origen o destino cerrado al publico. Ruta cancelada."

        cola = []
        distancias = {}

        for nodo in self.grafo:
            if nodo[1] == origen_fisico:
                if criterio == 1:
                    heapq.heappush(cola, (0, 4, nodo, [nodo]))
                    distancias[nodo] = (0, 4)
                else:
                    heapq.heappush(cola, (4, 0, nodo, [nodo]))
                    distancias[nodo] = (4, 0)

        while cola:
            costo_primario, costo_secundario, u, ruta = heapq.heappop(cola)
            linea_u, nombre_u = u

            if nombre_u == destino_fisico:
                ruta_nombres = []
                for n in ruta:
                    linea_ruta, nombre_ruta = n
                    if nombre_ruta in self.fallas_estaciones:
                        ruta_nombres.append(f"{nombre_ruta} ({linea_ruta}) [Pasa sin parar]")
                    else:
                        ruta_nombres.append(f"{nombre_ruta} ({linea_ruta})")
                ruta_str = ' -> '.join(ruta_nombres)

                if criterio == 1:
                    return f"\n--- RUTA OPTIMA ---\n{ruta_str}\nTransbordos: {costo_primario}\n-------------------"
                elif criterio == 2:
                    return f"\n--- RUTA OPTIMA ---\n{ruta_str}\nTiempo aprox: {costo_primario} mins\n-------------------"
                elif criterio == 3:
                    return f"\n--- RUTA OPTIMA ---\n{ruta_str}\nTiempo aprox: {costo_primario} mins | Transbordos: {costo_secundario}\n-------------------"

            for v, w_t, w_c in self.grafo.get(u, []):
                linea_v, nombre_v = v

                if frozenset({nombre_u, nombre_v}) in self.fallas_tramos:
                    continue

                if nombre_v in self.fallas_estaciones or nombre_u in self.fallas_estaciones:
                    if linea_u != linea_v:
                        continue

                tiempo_transicion = w_t + TIEMPO_TRANSBORDO if w_c == 1 else w_t
                transbordos_transicion = w_c

                if criterio == 1:
                    nuevo_estado = (costo_primario + transbordos_transicion, costo_secundario + tiempo_transicion)
                else:
                    nuevo_estado = (costo_primario + tiempo_transicion, costo_secundario + transbordos_transicion)

                if v not in distancias or nuevo_estado < distancias[v]:
                    distancias[v] = nuevo_estado
                    nueva_ruta = list(ruta)
                    nueva_ruta.append(v)
                    heapq.heappush(cola, (nuevo_estado[0], nuevo_estado[1], v, nueva_ruta))

        return "Ruta imposible de calcular. Cortes en la red no dejan alternativas."

    def evaluar_conectividad(self):
        """Evalúa la conectividad de la red mediante BFS y reporta componentes aislados."""
        nodos_operativos = {n for n in self.grafo if n[1] not in self.fallas_estaciones}
        if not nodos_operativos:
            return "Diagnostico P2: FALSO. Red muerta totalmente (todas las estaciones estan cerradas)."

        visitados_global = set()
        componentes = []

        for nodo_raiz in nodos_operativos:
            if nodo_raiz in visitados_global:
                continue

            componente_actual = set()
            cola = deque([nodo_raiz])
            visitados_global.add(nodo_raiz)

            while cola:
                u = cola.popleft()
                componente_actual.add(u)
                linea_u, nombre_u = u

                for v, _, _ in self.grafo.get(u, []):
                    if v in nodos_operativos and v not in visitados_global:
                        linea_v, nombre_v = v

                        if frozenset({nombre_u, nombre_v}) in self.fallas_tramos:
                            continue
                        if nombre_v in self.fallas_estaciones or nombre_u in self.fallas_estaciones:
                            if linea_u != linea_v:
                                continue

                        visitados_global.add(v)
                        cola.append(v)

            componentes.append(componente_actual)

        grupos_estaciones = []
        for comp in componentes:
            estaciones_nombres = sorted(list({n[1] for n in comp}))
            grupos_estaciones.append(estaciones_nombres)

        if len(componentes) == 1:
            return "Diagnostico P2: VERDADERO. La red sigue conectada (todas las estaciones operativas se alcanzan entre si)."
        else:
            resultado = "Diagnostico P2: FALSO. La red se ha segmentado en componentes desconectadas.\n"
            resultado += f"Se detectaron {len(componentes)} grupos independientes aislados entre sí:\n"
            for idx, grupo in enumerate(grupos_estaciones, 1):
                resultado += f"  -> Grupo {idx}: {', '.join(grupo)}\n"
            return resultado.strip()

    def _buscar_segmento_continuo(self, e1_real, e2_real):
        """Busca un camino continuo (sin transbordos) entre dos estaciones usando BFS.

        Solo sigue aristas con w_c == 0 (mismas línea), ignorando estaciones en falla.
        Retorna la lista de nodos del camino o None si no existe.
        """
        visitados = {e1_real}
        cola = deque([[e1_real]])
        ruta_encontrada = []

        while cola:
            camino_actual = cola.popleft()
            nodo_actual_nombre = camino_actual[-1]

            if nodo_actual_nombre == e2_real:
                ruta_encontrada = camino_actual
                break

            for nodo_u in self.grafo:
                if nodo_u[1] == nodo_actual_nombre:
                    for v, w_t, w_c in self.grafo.get(nodo_u, []):
                        if w_c == 0 and v[1] not in visitados:
                            visitados.add(v[1])
                            cola.append(camino_actual + [v[1]])

        return ruta_encontrada if ruta_encontrada else None

    def _declarar_cierre_estacion(self):
        """Cierra una estación: los trenes pasan de largo y se deshabilitan los transbordos."""
        est_ingresada = input("Nombre de la estacion a cerrar: ").strip()
        est_real = next((e for e in self.estaciones_fisicas if normalizar(e) == normalizar(est_ingresada)), None)
        if est_real:
            self.fallas_estaciones.add(est_real)
            print(f"[{est_real}] inhabilitada (Los trenes pasan de largo, transbordos deshabilitados).")
        else:
            print("Error: Estacion no encontrada.")

    def _declarar_cierre_tramo(self):
        """Cierra un tramo continuo entre dos estaciones de la misma línea."""
        e1_ing = input("Estacion de inicio del tramo: ").strip()
        e2_ing = input("Estacion de termino del tramo: ").strip()

        e1_real = next((e for e in self.estaciones_fisicas if normalizar(e) == normalizar(e1_ing)), None)
        e2_real = next((e for e in self.estaciones_fisicas if normalizar(e) == normalizar(e2_ing)), None)

        if e1_real and e2_real:
            ruta_encontrada = self._buscar_segmento_continuo(e1_real, e2_real)

            if ruta_encontrada:
                for i in range(len(ruta_encontrada) - 1):
                    self.fallas_tramos.add(frozenset({ruta_encontrada[i], ruta_encontrada[i + 1]}))
                print("Tramo bloqueado exitosamente.")
                if len(ruta_encontrada) > 2:
                    print(f"-> Macro-Tramo continuo aplicado en el trayecto: {' - '.join(ruta_encontrada)}")
            else:
                print(f"Error: No existe una via continua directa entre [{e1_real}] and [{e2_real}].")
        else:
            print("Error: Una o ambas estaciones no existen en la red.")

    def menu_principal(self):
        self.cargar_datos()
        while True:
            print("\n------------------------------")
            print("SISTEMA METRO DE SANTIAGO")
            print("------------------------------")
            print("1. Buscar ruta optima (P1)")
            print("2. Declarar contingencia (P2)")
            print("3. Salir")
            opcion = input("Elige una opcion: ").strip()

            if opcion == '1':
                origen = input("Estacion origen: ").strip()
                destino = input("Estacion destino: ").strip()
                print("Criterios disponibles: (1: Transbordos, 2: Tiempo, 3: Ambos simultaneamente)")
                criterio = input("Elige criterio: ").strip()
                if criterio in ['1', '2', '3']:
                    print("Calculando...")
                    print(self.calcular_ruta(origen, destino, int(criterio)))
                else:
                    print("Error: Criterio no valido.")

            elif opcion == '2':
                tipo = input("Tipo de falla (1: Estacion, 2: Tramo): ").strip()
                if tipo == '1':
                    self._declarar_cierre_estacion()
                elif tipo == '2':
                    self._declarar_cierre_tramo()
                else:
                    print("Opcion invalida.")
                    continue

                print("\nAnalizando estado topologico de la red...")
                print(self.evaluar_conectividad())

            elif opcion == '3':
                print("Saliendo del sistema...")
                break
            else:
                print("Comando no reconocido.")


if __name__ == "__main__":
    app = MetroRed()
    app.menu_principal()