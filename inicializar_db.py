# inicializar_db.py

import sys
import os
from datetime import datetime, timedelta
import random

# Asegúrate de que Python encuentre tus carpetas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importamos tu clase ya creada
from conexion.conexion_mongo import ConexionMongoDB

# === Inicializar conexión con MongoDB ===
conexion = ConexionMongoDB()
empleados = conexion.get_collection("empleados")
registros = conexion.get_collection("registros")

print(" Conexión establecida con MongoDB")


# === Función para calcular horas trabajadas ===
def calcular_horas_trabajadas(hora_entrada, hora_salida, max_horas_normales=8):
    formato = "%H:%M"
    entrada = datetime.strptime(hora_entrada, formato)
    salida = datetime.strptime(hora_salida, formato)
    diferencia = (salida - entrada).seconds / 3600  # En horas

    horas_normales = min(diferencia, max_horas_normales)
    horas_extras = max(diferencia - max_horas_normales, 0)

    return horas_normales, horas_extras


# === Empleados de ejemplo ===
empleados_lista = [
    {
        "nombre": "Juan Pérez",
        "dpi": "1234567890101",
        "cargo": "Desarrollador",
        "salario_hora": 85.50,
        "horario_entrada": "08:00",
        "horario_salida": "17:00"
    },
    {
        "nombre": "Ana López",
        "dpi": "9876543210123",
        "cargo": "Diseñadora",
        "salario_hora": 75.00,
        "horario_entrada": "09:00",
        "horario_salida": "18:00"
    },
    {
        "nombre": "Carlos Rojas",
        "dpi": "1112223334445",
        "cargo": "Ingeniero",
        "salario_hora": 90.00,
        "horario_entrada": "07:30",
        "horario_salida": "16:30"
    }
]

# === Insertar empleados en la base de datos ===
empleados.delete_many({})  # Limpiar antes de insertar (opcional)
empleados.insert_many(empleados_lista)
print(f" {len(empleados_lista)} empleados insertados correctamente")


# === Registrar entradas y salidas simuladas ===
def generar_registro_empleado(empleado, dias_atras=5):
    for i in range(dias_atras):
        fecha = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")

        # Generar hora de entrada y salida aleatoria (con ligera variación)
        entrada_base = "08:00"
        salida_base = "17:00"

        # Aleatorio entre 5 minutos antes o después
        offset_entrada = random.randint(-5, 10)
        offset_salida = random.randint(-5, 15)

        hora_entrada = (datetime.strptime(entrada_base, "%H:%M") + timedelta(minutes=offset_entrada)).strftime("%H:%M")
        hora_salida = (datetime.strptime(salida_base, "%H:%M") + timedelta(minutes=offset_salida)).strftime("%H:%M")

        # Calcular horas trabajadas
        horas_normales, horas_extras = calcular_horas_trabajadas(hora_entrada, hora_salida)
        pago_total = horas_normales * empleado["salario_hora"] + horas_extras * empleado["salario_hora"] * 1.5

        registro = {
            "dpi_empleado": empleado["dpi"],
            "fecha": fecha,
            "hora_entrada": hora_entrada,
            "hora_salida": hora_salida,
            "horas_normales": round(horas_normales, 2),
            "horas_extras": round(horas_extras, 2),
            "pago_total": round(pago_total, 2)
        }

        registros.insert_one(registro)

    print(f" Registros generados para {empleado['nombre']}")


# === Generar registros para todos los empleados ===
for emp in empleados.find():
    generar_registro_empleado(emp, dias_atras=5)

print("Base de datos inicializada exitosamente")