# gui_registro.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from conexion.conexion_mongo import ConexionMongoDB
from clases.empleado import Empleado


def abrir_registro_entrada_salida(app_root):
    ventana_registro = tk.Toplevel(app_root)
    ventana_registro.title("Registrar Entrada/Salida")
    ventana_registro.geometry("800x700")
    ventana_registro.configure(bg="#f9f9f9")

    # Título
    tk.Label(ventana_registro, text="Registrar Entrada/Salida", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=15)

    # Conectar a MongoDB
    conexion = ConexionMongoDB()
    empleados_collection = conexion.get_collection("empleados")
    empleados_lista = list(empleados_collection.find())

    if not empleados_lista:
        messagebox.showwarning("Advertencia", "No hay empleados registrados.")
        ventana_registro.destroy()
        return

    # Seleccionar empleado
    tk.Label(ventana_registro, text="Empleado:", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    combo_empleados = ttk.Combobox(
        ventana_registro,
        values=[f"{emp['nombre']} - {emp['dpi']}" for emp in empleados_lista],
        state="readonly",
        font=("Arial", 12)
    )
    combo_empleados.pack(pady=5)

    # Selector de fecha
    tk.Label(ventana_registro, text="Fecha:", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    fecha_entry = ttk.Entry(ventana_registro, font=("Arial", 12))
    fecha_entry.pack(pady=5)

    def seleccionar_fecha():
        top = tk.Toplevel(ventana_registro)
        top.title("Seleccionar Fecha")
        cal = DateEntry(top, width=12, background='darkblue', foreground='white', borderwidth=2,
                        year=2025, month=6, day=1, date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)

        def guardar_fecha():
            fecha_seleccionada = cal.get()
            fecha_entry.delete(0, tk.END)
            fecha_entry.insert(0, fecha_seleccionada)
            top.destroy()

        ttk.Button(top, text="Aceptar", command=guardar_fecha).pack(pady=10)

    ttk.Button(ventana_registro, text="Seleccionar Fecha", command=seleccionar_fecha).pack(pady=5)

    # Hora de entrada
    tk.Label(ventana_registro, text="Hora de entrada (HH:MM):", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    hora_entrada_entry = tk.Entry(ventana_registro, font=("Arial", 12))
    hora_entrada_entry.pack(pady=5)

    # Hora de salida
    tk.Label(ventana_registro, text="Hora de salida (HH:MM):", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    hora_salida_entry = tk.Entry(ventana_registro, font=("Arial", 12))
    hora_salida_entry.pack(pady=5)

    # Tipo de día
    tk.Label(ventana_registro, text="Tipo de día:", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    tipo_dia = ttk.Combobox(
        ventana_registro,
        values=["Día Normal", "Día Festivo", "Día de Descanso"],
        state="readonly",
        font=("Arial", 12)
    )
    tipo_dia.set("Día Normal")
    tipo_dia.pack(pady=5)

    # Botón Guardar
    def guardar_registro():
        seleccionado = combo_empleados.get()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un empleado.")
            return

        dpi = seleccionado.split(" - ")[-1]
        empleado_data = empleados_collection.find_one({"dpi": dpi})
        if not empleado_data:
            messagebox.showerror("Error", "Empleado no encontrado.")
            return

        fecha = fecha_entry.get().strip()
        hora_entrada = hora_entrada_entry.get().strip()
        hora_salida = hora_salida_entry.get().strip()
        tipo = tipo_dia.get()

        try:
            formato = "%H:%M"
            entrada = datetime.strptime(hora_entrada, formato)
            salida = datetime.strptime(hora_salida, formato)
            diferencia = (salida - entrada).seconds / 3600

            horas_normales = min(diferencia, 8)
            horas_extras = max(diferencia - 8, 0)

            salario_hora = empleado_data["salario_hora"]

            # Aplicar tarifas según tipo de día
            if tipo == "Día Festivo":
                pago_total = horas_normales * salario_hora * 2 + horas_extras * salario_hora * 3  # Ejemplo: festivo 2x y extra 3x
            elif tipo == "Día de Descanso":
                pago_total = 0  # No se paga si es día libre
            else:  # Día Normal
                pago_total = horas_normales * salario_hora + horas_extras * salario_hora * 1.5

            registro = {
                "dpi_empleado": dpi,
                "fecha": fecha,
                "hora_entrada": hora_entrada,
                "hora_salida": hora_salida,
                "horas_normales": round(horas_normales, 2),
                "horas_extras": round(horas_extras, 2),
                "tipo_dia": tipo,
                "pago_total": round(pago_total, 2)
            }

            registros_collection = conexion.get_collection("registros")
            registros_collection.insert_one(registro)
            messagebox.showinfo("Éxito", f"Registro guardado para {empleado_data['nombre']} - {fecha}")
            ventana_registro.destroy()

        except ValueError as e:
            messagebox.showerror("Formato inválido", f"Asegúrate de usar HH:MM correctamente.\n{e}")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo guardar el registro:\n{ex}")

    ttk.Button(ventana_registro, text="Guardar Registro", command=guardar_registro).pack(pady=20)

    # Opcional: Mostrar mensaje al final
    tk.Label(ventana_registro, text="Nota: Horas normales hasta 8 hrs. Extras se calculan después.",
             font=("Arial", 10, "italic"), bg="#f9f9f9", fg="#666").pack(pady=10)