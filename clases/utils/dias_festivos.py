from conexion.conexion_mongo import ConexionMongoDB


def cargar_dias_festivos():
    conexion = ConexionMongoDB()
    festivos = conexion.get_collection("dias_festivos")
    return [f["fecha"] for f in festivos.find({}, {"fecha": 1})]


def es_festivo(fecha_str):
    dias_festivos = cargar_dias_festivos()
    return fecha_str in dias_festivos