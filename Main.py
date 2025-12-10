import os
from datetime import datetime
from clases.gestion_personal import GestionPersonal
from clases.empleado import Empleado
from clases.registro import Registro
from conexion.conexion_mongo import ConexionMongoDB


def limpiar_pantalla():
    """Limpia la consola para mejorar la experiencia de usuario"""
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_menu():
    print("===  Menú Principal - Sistema de Control de Personal ===")
    print("1. Ver lista de empleados")
    print("2. Registrar entrada/salida")
    print("3. Generar reporte de horas trabajadas")
    print("4. Salir")
    print("==========================================================")


def ver_empleados():
    conexion = ConexionMongoDB()
    empleados = conexion.get_collection("empleados")
    
    print("\n👥 Lista de empleados:")
    for emp in empleados.find():
        print(f"DPI: {emp['dpi']} | Nombre: {emp['nombre']} | Cargo: {emp['cargo']} | Salario/hora: Q{emp['salario_hora']}")
    print()

def registrar_entrada_salida():
    dpi = input("\nIngrese el DPI del empleado: ")
    
    conexion = ConexionMongoDB()
    empleados = conexion.get_collection("empleados")
    registros = conexion.get_collection("registros")

    empleado_data = empleados.find_one({"dpi": dpi})
    if not empleado_data:
        print(" Empleado no encontrado.\n")
        return

    empleado = Empleado.from_dict(empleado_data)
    print(f" Empleado encontrado: {empleado.nombre}")

    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    hora_entrada = input("Ingrese la hora de entrada (ej. 08:02): ")
    hora_salida = input("Ingrese la hora de salida (ej. 17:45): ")

    # Calcular horas trabajadas
    formato = "%H:%M"
    entrada = datetime.strptime(hora_entrada, formato)
    salida = datetime.strptime(hora_salida, formato)
    diferencia = (salida - entrada).seconds / 3600  # En horas

    horas_normales = min(diferencia, 8)
    horas_extras = max(diferencia - 8, 0)
    pago_total = horas_normales * empleado.salario_hora + horas_extras * empleado.salario_hora * 1.5

    # Guardar registro
    registro = {
        "dpi_empleado": empleado.dpi,
        "fecha": fecha_actual,
        "hora_entrada": hora_entrada,
        "hora_salida": hora_salida,
        "horas_normales": round(horas_normales, 2),
        "horas_extras": round(horas_extras, 2),
        "pago_total": round(pago_total, 2)
    }

    registros.insert_one(registro)
    print(f"\n Registro guardado exitosamente para {empleado.nombre} - Fecha: {fecha_actual}")
    print(f"Horas normales: {horas_normales:.2f} hrs")
    print(f"Horas extras: {horas_extras:.2f} hrs")
    print(f"Pago total: Q{pago_total:.2f}\n")


def generar_reporte():
    dpi = input("\nIngrese el DPI del empleado: ")

    conexion = ConexionMongoDB()
    empleados = conexion.get_collection("empleados")
    registros = conexion.get_collection("registros")

    empleado_data = empleados.find_one({"dpi": dpi})
    if not empleado_data:
        print(" Empleado no encontrado.\n")
        return

    empleado = Empleado.from_dict(empleado_data)

    mes = input("Ingrese el mes y año (ej. 2024-10): ")
    filtro = {
        "dpi_empleado": dpi,
        "fecha": {"$regex": f"^{mes}"}
    }

    resultados = list(registros.find(filtro))
    if not resultados:
        print(" No se encontraron registros para este periodo.")
        return

    total_horas_normales = sum(r["horas_normales"] for r in resultados)
    total_horas_extras = sum(r["horas_extras"] for r in resultados)
    total_pago = sum(r["pago_total"] for r in resultados)

    print(f"\n Reporte mensual para {empleado.nombre} ({mes})")
    print(f"Total horas normales: {total_horas_normales:.2f} hrs")
    print(f"Total horas extras: {total_horas_extras:.2f} hrs")
    print(f"Pago total: Q{total_pago:.2f}\n")


def main():
    while True:
        limpiar_pantalla()
        mostrar_menu()
        opcion = input("Seleccione una opción (1-4): ")

        if opcion == "1":
            limpiar_pantalla()
            print("=== Ver lista de empleados ===\n")
            ver_empleados()
            input("Presione Enter para continuar...")

        elif opcion == "2":
            limpiar_pantalla()
            print("=== Registrar entrada/salida ===\n")
            registrar_entrada_salida()
            input("Presione Enter para continuar...")

        elif opcion == "3":
            limpiar_pantalla()
            print("=== Generar reporte mensual ===\n")
            generar_reporte()
            input("Presione Enter para continuar...")

        elif opcion == "4":
            print("\n ¡Gracias por usar el sistema! Hasta pronto.\n")
            break

        else:
            print("\n Opción no válida. Intente nuevamente.")
            input("Presione Enter para continuar...")


if __name__ == "__main__":
    main()