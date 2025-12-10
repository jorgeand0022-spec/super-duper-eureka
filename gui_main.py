# gui_main.py
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# Importamos tus clases existentes
from conexion.conexion_mongo import ConexionMongoDB
from clases.empleado import Empleado
from backup_mongodb import realizar_respaldo, restaurar_respaldo


#carpeta raiz 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Control de Personal")
        self.geometry("800x500")
        self.resizable(False, False)
        self.configure(bg="#f2f2f2")
        
        # Estilo moderno
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=10, relief="flat",
                             background="#4CAF50", foreground="white", font=("Arial", 12))
        self.style.map("TButton", background=[("active", "#45a049")])
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        self.style.configure("Treeview", rowheight=25, font=("Arial", 11))

        # Variable para guardar el rol del usuario logueado
        self.rol_usuario = None
        self.withdraw()

    def mostrar_menu_principal(self, rol):
        """Muestra el menú principal según el rol"""
        self.withdraw()  # Ocultar ventana de login
        self.deiconify()  # Mostrar ventana principal
        self.rol_usuario = rol
        self.create_widgets_with_role(rol)

    def create_widgets_with_role(self, rol):
        """Crea los widgets según el rol del usuario"""
        # Título principal
        title_label = tk.Label(self, text="Sistema de Control de Personal", font=("Arial", 16, "bold"),
                               bg="#f2f2f2", fg="#333")
        title_label.pack(pady=30)

        btn_frame = tk.Frame(self, bg="#f2f2f2")
        btn_frame.pack(pady=20)
        
    
        if rol in "administrador":
            ttk.Button(btn_frame, text="Gestionar Empleados", width=30,
                       command=self.abrir_gestion_empleados).grid(row=0, column=0, padx=10, pady=10)

        if rol in ["administrador", "supervisor"]:
            ttk.Button(btn_frame, text="Registrar Entrada/Salida", width=30,
                       command=self.abrir_registro_entrada_salida).grid(row=1, column=0, padx=10, pady=10)

        if rol in ["administrador", "supervisor", "empleado"]:
            ttk.Button(btn_frame, text="Generar Reporte Mensual", width=30,
                       command=self.abrir_ventana_reporte).grid(row=2, column=0, padx=10, pady=10)

        if rol == "administrador":
            ttk.Button(btn_frame, text="Restaurar Respaldo", width=30,
               command=self.restaurar_respaldo).grid(row=4, column=0, padx=10, pady=10)
    
        ttk.Button(btn_frame, text="Salir", width=30, command=self.destroy).grid(row=3, column=0, padx=10, pady=10)
    
    def salir_con_respaldo(self):
        from backup_mongodb import realizar_respaldo
        realizar_respaldo()
        self.destroy()
    
    def restaurar_respaldo(self):
     from tkinter import filedialog
     ruta = filedialog.askopenfilename(
         title="Seleccionar archivo de respaldo",
         initialdir="respaldos/",
         filetypes=[("Archivos JSON", "*.json")]
     )
     if not ruta:
        return

     resultado = restaurar_respaldo(ruta)
     if resultado:
         self.cargar_empleados()
         messagebox.showinfo("Éxito", "Respaldo restaurado correctamente.")
     else:
         messagebox.showerror("Error", "No se pudo restaurar el respaldo.")
    

    def abrir_gestion_empleados(self):
        ventana_lista = tk.Toplevel(self)
        ventana_lista.title("Lista de Empleados")
        ventana_lista.geometry("900x600")
        ventana_lista.configure(bg="#ffffff")

        tk.Label(ventana_lista, text="Lista de Empleados", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        btn_frame = tk.Frame(ventana_lista, bg="#ffffff")
        btn_frame.pack(pady=10)

        btn_agregar = ttk.Button(btn_frame, text="Agregar Empleado", width=25, command=self.agregar_empleado)
        btn_editar = ttk.Button(btn_frame, text="Editar Seleccionado", width=25, command=self.editar_empleado)
        btn_pdf = ttk.Button(btn_frame, text="Exportar a PDF", width=25, command=self.exportar_a_pdf)
        btn_eliminar = ttk.Button(btn_frame, text="Eliminar Seleccionado", width=25, command=self.eliminar_empleado)

        btn_agregar.grid(row=0, column=0, padx=10)
        btn_editar.grid(row=0, column=1, padx=10)
        btn_pdf.grid(row=0, column=2, padx=10)
        btn_eliminar.grid(row=0, column=3, padx=10)

        # Tabla de empleados
        self.tree = ttk.Treeview(ventana_lista,
                                 columns=("DPI", "Nombre", "Cargo", "Salario/Hora"),
                                 show="headings", height=20)
        self.tree.heading("DPI", text="DPI")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Cargo", text="Cargo")
        self.tree.heading("Salario/Hora", text="Salario por Hora")

        self.tree.column("DPI", width=150, anchor="center")
        self.tree.column("Nombre", width=250, anchor="w")
        self.tree.column("Cargo", width=250, anchor="w")
        self.tree.column("Salario/Hora", width=150, anchor="e")

        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        self.cargar_empleados()

        # Doble clic para editar
        self.tree.bind("<Double-1>", lambda event: self.editar_empleado())

    def cargar_empleados(self):
        """Carga los empleados desde MongoDB"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        conexion = ConexionMongoDB()
        empleados_collection = conexion.get_collection("empleados")
        empleados = list(empleados_collection.find())

        for emp in empleados:
            self.tree.insert("", tk.END, values=(
                emp["dpi"],
                emp["nombre"],
                emp["cargo"],
                f"${emp['salario_hora']:.2f}"
            ))

    def agregar_empleado(self):
        self.abrir_formulario_edicion()

    def editar_empleado(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Seleccionar", "Por favor, seleccione un empleado.")
            return

        valores = self.tree.item(selected, 'values')
        dpi_seleccionado = valores[0]
        self.abrir_formulario_edicion(dpi_seleccionado)

    def eliminar_empleado(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Seleccionar", "Por favor, seleccione un empleado.")
            return

        valores = self.tree.item(selected, 'values')
        dpi_seleccionado = valores[0]

        if messagebox.askyesno("Eliminar", f"¿Está seguro de eliminar a {valores[1]}?"):
            conexion = ConexionMongoDB()
            empleados = conexion.get_collection("empleados")
            empleados.delete_one({"dpi": dpi_seleccionado})
            self.cargar_empleados()
            messagebox.showinfo("Éxito", "Empleado eliminado correctamente.")

    def abrir_formulario_edicion(self, dpi=None):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar/Editar Empleado")
        ventana.geometry("500x400")
        ventana.configure(bg="#ffffff")

        tk.Label(ventana, text="Nombre:", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        nombre_entry = tk.Entry(ventana, font=("Arial", 12))
        nombre_entry.pack(pady=5)

        tk.Label(ventana, text="DPI:", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        dpi_entry = tk.Entry(ventana, font=("Arial", 12))
        dpi_entry.pack(pady=5)

        tk.Label(ventana, text="Cargo:", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        cargo_entry = tk.Entry(ventana, font=("Arial", 12))
        cargo_entry.pack(pady=5)

        tk.Label(ventana, text="Salario por hora:", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        salario_entry = tk.Entry(ventana, font=("Arial", 12))
        salario_entry.pack(pady=5)

        if dpi:
            # Cargar datos existentes
            conexion = ConexionMongoDB()
            empleado_data = conexion.get_collection("empleados").find_one({"dpi": dpi})
            if empleado_data:
                nombre_entry.insert(0, empleado_data["nombre"])
                dpi_entry.insert(0, empleado_data["dpi"])
                cargo_entry.insert(0, empleado_data["cargo"])
                salario_entry.insert(0, str(empleado_data["salario_hora"]))

        def guardar():
            nombre = nombre_entry.get()
            dpi = dpi_entry.get()
            cargo = cargo_entry.get()
            try:
                salario = float(salario_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Ingrese un salario válido.")
                return

            if not all([nombre, dpi, cargo]):
                messagebox.showerror("Error", "Complete todos los campos.")
                return

            empleado = Empleado(nombre, dpi, cargo, salario)

            conexion = ConexionMongoDB()
            empleados = conexion.get_collection("empleados")

            if dpi and empleados.find_one({"dpi": dpi}):
                # Actualizar
                empleados.update_one({"dpi": dpi}, {"$set": empleado.to_dict()})
                messagebox.showinfo("Éxito", "Empleado actualizado correctamente.")
            else:
                # Crear nuevo
                empleados.insert_one(empleado.to_dict())
                messagebox.showinfo("Éxito", "Empleado agregado correctamente.")

            self.cargar_empleados()
            ventana.destroy()

        ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=20)

    def exportar_a_pdf(self):
        conexion = ConexionMongoDB()
        empleados = list(conexion.get_collection("empleados").find())

        if not empleados:
            messagebox.showwarning("Advertencia", "No hay empleados registrados.")
            return

        archivo = "lista_empleados.pdf"
        doc = SimpleDocTemplate(archivo, pagesize=letter)
        estilo = getSampleStyleSheet()
        elementos = []

        elementos.append(Paragraph("Lista de Empleados", estilo["Title"]))
        elementos.append(Spacer(1, 24))

        data = [["DPI", "Nombre", "Cargo", "Salario/Hora"]]
        for emp in empleados:
            data.append([
                emp["dpi"],
                emp["nombre"],
                emp["cargo"],
                f"${emp['salario_hora']:.2f}"
            ])

        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#f9f9f9'),
            ('GRID', (0, 0), (-1, -1), 1, '#cccccc')
        ]))

        elementos.append(tabla)
        doc.build(elementos)
        messagebox.showinfo("PDF Generado", f"Archivo guardado como '{archivo}'")

    def abrir_registro_entrada_salida(self):
        from gui_registro import abrir_registro_entrada_salida
        abrir_registro_entrada_salida(self)

    def abrir_ventana_reporte(self):
        from gui_reporte import abrir_ventana_reporte
        abrir_ventana_reporte(self)

if __name__ == "__main__":
    app = App()
    app.withdraw()  # Ocultar hasta que inicie sesión
    from gui_login import abrir_ventana_login
    abrir_ventana_login(app)
    app.mainloop()