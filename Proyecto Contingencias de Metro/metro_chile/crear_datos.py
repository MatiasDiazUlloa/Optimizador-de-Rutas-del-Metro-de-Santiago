lines = {
    "L1": ["San Pablo", "Neptuno", "Pajaritos", "Las Rejas", "Ecuador", "San Alberto Hurtado", "Universidad de Santiago", "Estacion Central", "Union Latinoamericana", "Republica", "Los Heroes", "La Moneda", "Universidad de Chile", "Santa Lucia", "Universidad Catolica", "Baquedano", "Salvador", "Manuel Montt", "Pedro de Valdivia", "Los Leones", "Tobalaba", "El Golf", "Alcantara", "Escuela Militar", "Manquehue", "Hernando de Magallanes", "Los Dominicos"],
    "L2": ["Vespucio Norte", "Zapadores", "Dorsal", "Einstein", "Cementerios", "Cerro Blanco", "Patronato", "Puente Cal y Canto", "Santa Ana", "Los Heroes", "Toesca", "Parque OHiggins", "Rondizzoni", "Franklin", "El Llano", "San Miguel", "Lo Vial", "Departamental", "Ciudad del Nino", "Lo Ovalle", "El Parron", "La Cisterna", "El Bosque", "Observatorio", "Copa Lo Martinez", "Hospital El Pino"],
    "L3": ["Plaza Quilicura", "Lo Cruzat", "Ferrocarril", "Los Libertadores", "Cardenal Caro", "Vivaceta", "ConchalI", "Plaza Chacabuco", "Hospitales", "Puente Cal y Canto", "Plaza de Armas", "Universidad de Chile", "Parque Almagro", "Matta", "Irrazaval", "Monsenor Eyzaguirre", "Nunoa", "Chile Espana", "Villa Frei", "Plaza Egaña", "Fernando Castillo Velasco"],
    "L4": ["Tobalaba", "Cristobal Colon", "Francisco Bilbao", "Principe de Gales", "Simon Bolivar", "Plaza Egaña", "Los Orientales", "Grecia", "Los Presidentes", "Quilin", "Las Torres", "Macul", "Vicuna Mackenna", "Vicente Valdes", "Rojas Magallanes", "Trinidad", "San Jose de la Estrella", "Los Quillayes", "Elisa Correa", "Hospital Sotero del Rio", "Protectora de la Infancia", "Las Mercedes", "Plaza de Puente Alto"],
    "L4A": ["La Cisterna", "San Ramon", "Santa Rosa", "La Granja", "Santa Julia", "Vicuna Mackenna"],
    "L5": ["Plaza de Maipu", "Santiago Bueras", "Del Sol", "Monte Tabor", "Las Parcelas", "Laguna Sur", "Barrancas", "Pudahuel", "San Pablo", "Lo Prado", "Blanqueado", "Gruta de Lourdes", "Quinta Normal", "Cumming", "Santa Ana", "Plaza de Armas", "Bellas Artes", "Baquedano", "Parque Bustamante", "Santa Isabel", "Irrazaval", "Nuble", "Rodrigo de Araya", "Carlos Valdovinos", "Camino Agricola", "San Joaquin", "Pedrero", "Mirador", "Bellavista de La Florida", "Vicente Valdes"],
    "L6": ["Cerrillos", "Lo Valledor", "Presidente Pedro Aguirre Cerda", "Franklin", "Bio Bio", "Nuble", "Estadio Nacional", "Nunoa", "Ines de Suarez", "Los Leones"]
}

all_stations = set()
for line, stations in lines.items():
    for s in stations:
        all_stations.add(s)
with open("metro_chile/estaciones_mx.txt", "w", encoding="utf-8") as f:
    for s in sorted(all_stations):
        f.write(s + "\n")

with open("metro_chile/vias_mx.txt", "w", encoding="utf-8") as f:
    for line, stations in sorted(lines.items()):
        for i in range(len(stations) - 1):
            f.write(f"{line},{stations[i]},{line},{stations[i+1]},2\n")

transfers = [
    ("L1", "San Pablo", "L5", "San Pablo", 6),
    ("L1", "Los Heroes", "L2", "Los Heroes", 6),
    ("L1", "Universidad de Chile", "L3", "Universidad de Chile", 6),
    ("L1", "Baquedano", "L5", "Baquedano", 6),
    ("L1", "Los Leones", "L6", "Los Leones", 6),
    ("L1", "Tobalaba", "L4", "Tobalaba", 6),
    ("L2", "Santa Ana", "L5", "Santa Ana", 6),
    ("L2", "Puente Cal y Canto", "L3", "Puente Cal y Canto", 6),
    ("L2", "Franklin", "L6", "Franklin", 6),
    ("L2", "La Cisterna", "L4A", "La Cisterna", 6),
    ("L3", "Plaza de Armas", "L5", "Plaza de Armas", 6),
    ("L3", "Irrazaval", "L5", "Irrazaval", 6),
    ("L3", "Nunoa", "L6", "Nunoa", 6),
    ("L3", "Plaza Egaña", "L4", "Plaza Egaña", 6),
    ("L4", "Vicuna Mackenna", "L4A", "Vicuna Mackenna", 6),
    ("L4", "Vicente Valdes", "L5", "Vicente Valdes", 6),
    ("L5", "San Pablo", "L1", "San Pablo", 6),
    ("L5", "Santa Ana", "L2", "Santa Ana", 6),
    ("L5", "Baquedano", "L1", "Baquedano", 6),
    ("L5", "Nuble", "L6", "Nuble", 6),
    ("L5", "Vicente Valdes", "L4", "Vicente Valdes", 6),
    ("L6", "Franklin", "L2", "Franklin", 6),
    ("L6", "Nunoa", "L3", "Nunoa", 6),
    ("L6", "Los Leones", "L1", "Los Leones", 6),
    ("L4A", "La Cisterna", "L2", "La Cisterna", 6),
    ("L4A", "Vicuna Mackenna", "L4", "Vicuna Mackenna", 6),
]
with open("metro_chile/vias_mx.txt", "a", encoding="utf-8") as f:
    for l1, e1, l2, e2, w in transfers:
        f.write(f"{l1},{e1},{l2},{e2},{w}\n")

print(f"Estaciones unicas: {len(all_stations)}")
print(f"Líneas: {len(lines)}")
with open("metro_chile/vias_mx.txt", "r", encoding="utf-8") as f:
    print(f"Total vías: {len(f.readlines())}")
