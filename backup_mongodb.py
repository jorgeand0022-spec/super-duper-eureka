# backup_utils.py
from pymongo import MongoClient
import os
import json
import datetime

MONGO_URI = "mongodb+srv://LuisBueno23:Luis2020@clusterlbm.66uyt.mongodb.net/control_personal?retryWrites=true&w=majority"

def realizar_respaldo():
    """Realiza un respaldo automático de todas las colecciones"""
    client = MongoClient(MONGO_URI)
    db = client["control_personal"]

    directorio_backup = "respaldos"
    if not os.path.exists(directorio_backup):
        os.makedirs(directorio_backup)

    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

    for coleccion in ["empleados", "registros", "usuarios"]:
        datos = list(db[coleccion].find({}))
        nombre_archivo = os.path.join(directorio_backup, f"{coleccion}_{fecha_actual}.json")
        with open(nombre_archivo, "w", encoding="utf-8") as file:
            json.dump(datos, file, indent=4, default=str)

    limpiar_antiguos_respaldo(directorio_backup)
    print(" Respaldo realizado exitosamente")


def limpiar_antiguos_respaldo(directorio):
    """Mantiene solo los 3 respaldos más recientes"""
    archivos = [os.path.join(directorio, f) for f in os.listdir(directorio) if f.endswith(".json")]
    archivos.sort(key=os.path.getmtime)
    while len(archivos) > 3:
        os.remove(archivos.pop(0))


def restaurar_respaldo(ruta_json):
    """Restaura una base de datos desde un archivo JSON"""
    try:
        client = MongoClient(MONGO_URI)
        db = client["control_personal"]
        with open(ruta_json, "r", encoding="utf-8") as file:
            datos = json.load(file)

        
        coleccion_nombre = ruta_json.split("_")[0].split(os.sep)[-1]

        # Limpiar colección actual
        db[coleccion_nombre].delete_many({})
        documentos = []
        for doc in datos:
            if "_id" in doc:
                del doc["_id"]
            documentos.append(doc)

        if documentos:
            db[coleccion_nombre].insert_many(documentos)
        return True
    except Exception as e:
        print(f" Error al restaurar: {e}")
        return False