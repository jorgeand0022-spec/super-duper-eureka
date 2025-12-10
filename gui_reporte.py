 # gui_reporte.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from conexion.conexion_mongo import ConexionMongoDB
from clases.empleado import Empleado


def abrir_ventana_reporte(app_root):
    ventana_reporte = tk.Toplevel(app_root)
    ventana_reporte.title("Generar Reporte")
    ventana_reporte.geometry("700x500")
    ventana_reporte.configure(bg="#f9f9f9")

    # Título
    tk.Label(ventana_reporte, text="Generar Reporte de Horas Trabajadas", font=("Arial", 14, "bold"),
             bg="#f9f9f9").pack(pady=15)

    # Seleccionar empleado(s)
    tk.Label(ventana_reporte, text="Seleccionar Empleado(s):", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)

    frame_empleados = tk.Frame(ventana_reporte, bg="#f9f9f9")
    frame_empleados.pack(pady=5)

    # Cargar empleados desde MongoDB
    conexion = ConexionMongoDB()
    empleados_collection = conexion.get_collection("empleados")
    empleados_lista = list(empleados_collection.find())
    nombres_dpi = [f"{emp['nombre']} - {emp['dpi']}" for emp in empleados_lista]

    if not empleados_lista:
        messagebox.showwarning("Advertencia", "No hay empleados registrados.")
        ventana_reporte.destroy()
        return

    # Checkbox para seleccionar todos
    var_todos = tk.BooleanVar()
    check_todos = tk.Checkbutton(frame_empleados, text="Todos los empleados",
                                 variable=var_todos, onvalue=True, offvalue=False,
                                 bg="#f9f9f9", font=("Arial", 12))
    check_todos.pack(anchor="w")

    # Lista de checkboxes
    var_dict = {}
    for nombre_dpi in nombres_dpi:
        var = tk.BooleanVar()
        tk.Checkbutton(frame_empleados, text=nombre_dpi, variable=var, onvalue=True, offvalue=False,
                       bg="#f9f9f9", font=("Arial", 11)).pack(anchor="w")
        var_dict[nombre_dpi] = var

    # Selector de rango de tiempo
    tk.Label(ventana_reporte, text="Rango de Tiempo:", font=("Arial", 12), bg="#f9f9f9").pack(pady=10)
    rango_seleccion = ttk.Combobox(ventana_reporte, values=["Día", "Semana", "Mes"], state="readonly",
                                   font=("Arial", 12))
    rango_seleccion.set("Mes")
    rango_seleccion.pack(pady=5)

    # Campo de fecha
    tk.Label(ventana_reporte, text="Fecha (ej. 2025-06):", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    fecha_entry = tk.Entry(ventana_reporte, font=("Arial", 12))
    fecha_entry.pack(pady=5)

    def generar():
        seleccionados = []

        if var_todos.get():
            seleccionados = empleados_lista
        else:
            for nombre_dpi, var in var_dict.items():
                if var.get():
                    dpi = nombre_dpi.split(" - ")[1]
                    emp = empleados_collection.find_one({"dpi": dpi})
                    if emp:
                        seleccionados.append(emp)

        if not seleccionados:
            messagebox.showerror("Error", "Seleccione al menos un empleado.")
            return

        rango = rango_seleccion.get()
        fecha_str = fecha_entry.get().strip()

        try:
            if rango == "Día":
                filtro_fecha = {"fecha": fecha_str}
            elif rango == "Semana":
                # Ejemplo: ingreso "2025-06-10" → filtra del lunes al domingo de esa semana
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                inicio = fecha - timedelta(days=fecha.weekday())
                fin = inicio + timedelta(days=6)
                filtro_fecha = {
                    "fecha": {
                        "$gte": inicio.strftime("%Y-%m-%d"),
                        "$lte": fin.strftime("%Y-%m-%d")
                    }
                }
            elif rango == "Mes":
                # Ejemplo: ingreso "2025-06" → filtra ese mes
                filtro_fecha = {"fecha": {"$regex": f"^{fecha_str}"}}
        except Exception as e:
            messagebox.showerror("Error", f"Fecha inválida: {e}")
            return

        resultados_completos = []
        for emp in seleccionados:
            filtro = {"dpi_empleado": emp["dpi"]}
            filtro.update(filtro_fecha)
            registros = conexion.get_collection("registros").find(filtro).sort("fecha", 1)

            total_horas_normales = 0
            total_horas_extras = 0
            total_pago = 0

            for reg in registros:
                total_horas_normales += reg["horas_normales"]
                total_horas_extras += reg["horas_extras"]
                total_pago += reg["pago_total"]

            resultados_completos.append({
                "nombre": emp["nombre"],
                "dpi": emp["dpi"],
                "total_horas_normales": round(total_horas_normales, 2),
                "total_horas_extras": round(total_horas_extras, 2),
                "total_pago": round(total_pago, 2)
            })

        mostrar_resultados(ventana_reporte, resultados_completos, app_root)

    ttk.Button(ventana_reporte, text="Generar Reporte", command=generar).pack(pady=15)

    # Botón Exportar a PDF
    def exportar():
        seleccionados = []

        if var_todos.get():
            seleccionados = empleados_lista
        else:
            for nombre_dpi, var in var_dict.items():
                if var.get():
                    dpi = nombre_dpi.split(" - ")[1]
                    emp = empleados_collection.find_one({"dpi": dpi})
                    if emp:
                        seleccionados.append(emp)

        if not seleccionados:
            messagebox.showerror("Error", "Seleccione al menos un empleado.")
            return

        rango = rango_seleccion.get()
        fecha_str = fecha_entry.get().strip()

        try:
            if rango == "Día":
                filtro_fecha = {"fecha": fecha_str}
            elif rango == "Semana":
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                inicio = fecha - timedelta(days=fecha.weekday())
                fin = inicio + timedelta(days=6)
                filtro_fecha = {
                    "fecha": {
                        "$gte": inicio.strftime("%Y-%m-%d"),
                        "$lte": fin.strftime("%Y-%m-%d")
                    }
                }
            elif rango == "Mes":
                filtro_fecha = {"fecha": {"$regex": f"^{fecha_str}"}}

        except Exception as e:
            messagebox.showerror("Error", f"Fecha inválida: {e}")
            return

        resultados_completos = []
        for emp in seleccionados:
            filtro = {"dpi_empleado": emp["dpi"]}
            filtro.update(filtro_fecha)
            registros = conexion.get_collection("registros").find(filtro).sort("fecha", 1)

            total_horas_normales = 0
            total_horas_extras = 0
            total_pago = 0

            for reg in registros:
                total_horas_normales += reg["horas_normales"]
                total_horas_extras += reg["horas_extras"]
                total_pago += reg["pago_total"]

            resultados_completos.append({
                "nombre": emp["nombre"],
                "dpi": emp["dpi"],
                "total_horas_normales": round(total_horas_normales, 2),
                "total_horas_extras": round(total_horas_extras, 2),
                "total_pago": round(total_pago, 2)
            })

        exportar_a_pdf(resultados_completos, ventana_reporte)

    ttk.Button(ventana_reporte, text="Exportar a PDF", command=exportar).pack(pady=10)


def mostrar_resultados(root, resultados, app_root):
    ventana_detalle = tk.Toplevel(app_root)
    ventana_detalle.title("Reporte Generado")
    ventana_detalle.geometry("1920x1080")
    ventana_detalle.configure(bg="#ffffff")

    tk.Label(ventana_detalle, text="Resultados del Reporte", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

    tree = ttk.Treeview(ventana_detalle,
                         columns=("Nombre", "Horas Normales", "Horas Extras", "Pago Total"),
                         show="headings", height=15)
    tree.heading("Nombre", text="Nombre")
    tree.heading("Horas Normales", text="Horas Normales")
    tree.heading("Horas Extras", text="Horas Extras")
    tree.heading("Pago Total", text="Pago Total")

    tree.column("Nombre", width=200, anchor="w")
    tree.column("Horas Normales", width=150, anchor="center")
    tree.column("Horas Extras", width=150, anchor="center")
    tree.column("Pago Total", width=150, anchor="e")

    for res in resultados:
        tree.insert("", tk.END, values=(
            res["nombre"],
            res["total_horas_normales"],
            res["total_horas_extras"],
            f"Q{res['total_pago']:.2f}"
        ))

    tree.pack(padx=20, pady=10, fill="both", expand=True)

    ttk.Button(ventana_detalle, text="Cerrar", command=ventana_detalle.destroy).pack(pady=10)


def exportar_a_pdf(resultados, root_window):
    archivo = "reporte_personal_detallado.pdf"
    doc = SimpleDocTemplate(archivo, pagesize=letter)
    estilo = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph("Reporte Detallado de Horas Trabajadas", estilo["Title"]))
    elementos.append(Spacer(1, 24))

    # Tabla resumen general
    data_resumen = [["Empleado", "Horas Normales", "Horas Extras", "Pago Total"]]
    for res in resultados:
        data_resumen.append([
            res["nombre"],
            str(res["total_horas_normales"]),
            str(res["total_horas_extras"]),
            f"Q{res['total_pago']:.2f}"
        ])

    tabla_resumen = Table(data_resumen)
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#f9f9f9'),
        ('GRID', (0, 0), (-1, -1), 1, '#cccccc')
    ]))
    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 30))

    # Detalles por empleado
    registros_collection = ConexionMongoDB().get_collection("registros")

    for res in resultados:
        elementos.append(Paragraph(f"Detalles de {res['nombre']} ({res['dpi']})", estilo["Heading2"]))
        data_detalle = [["Fecha", "Entrada", "Salida", "Normales", "Extras", "Tipo Día", "Pago"]]

        filtro = {"dpi_empleado": res["dpi"]}
        registros = registros_collection.find(filtro).sort("fecha", 1)

        for reg in registros:
            data_detalle.append([
                reg["fecha"],
                reg["hora_entrada"],
                reg["hora_salida"],
                str(reg["horas_normales"]),
                str(reg["horas_extras"]),
                reg.get("tipo_dia", "No definido"),
                f"Q{reg['pago_total']:.2f}"
            ])

        tabla_detalle = Table(data_detalle)
        tabla_detalle.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#808080'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
            ('GRID', (0, 0), (-1, -1), 1, '#cccccc')
        ]))
        elementos.append(tabla_detalle)
        elementos.append(Spacer(1, 20))

    doc.build(elementos)
    messagebox.showinfo("PDF Generado", f"Archivo guardado como '{archivo}'")