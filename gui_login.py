# gui_login.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.auth import validar_credenciales


def abrir_ventana_login(app_root):
    ventana_login = tk.Toplevel(app_root)
    ventana_login.title("Iniciar Sesión")
    ventana_login.geometry("400x300")
    ventana_login.configure(bg="#f9f9f9")

    tk.Label(ventana_login, text="Inicio de Sesión", font=("Arial", 16, "bold"), bg="#f9f9f9").pack(pady=20)

    tk.Label(ventana_login, text="Usuario:", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    usuario_entry = tk.Entry(ventana_login, font=("Arial", 12))
    usuario_entry.pack(pady=5)

    tk.Label(ventana_login, text="Contraseña:", font=("Arial", 12), bg="#f9f9f9").pack(pady=5)
    password_entry = tk.Entry(ventana_login, show="*", font=("Arial", 12))
    password_entry.pack(pady=5)

    def iniciar_sesion():
        usuario = usuario_entry.get().strip()
        contraseña = password_entry.get().strip()

        rol = validar_credenciales(usuario, contraseña)
        if rol:
            ventana_login.destroy()
            app_root.rol_usuario = rol
            app_root.mostrar_menu_principal(rol)  # ✅ Llamamos al método de la clase App
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    ttk.Button(ventana_login, text="Iniciar Sesión", command=iniciar_sesion).pack(pady=20)