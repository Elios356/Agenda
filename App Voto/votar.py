import customtkinter as ctk
import os
import requests
import re
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt

from db import BaseDeDatos
from correos_permitidos import VerificadorCorreo

# --- CONFIGURACIÓN VISUAL ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_FONDO = "#0F172A"
COLOR_CARD = "#1E293B"
COLOR_ACCENTO = "#38BDF8"
ADMIN_PASSWORD = "admin123"

# Reemplaza con tu URL de Make
URL_MAKE_WEBHOOK = "https://hook.make.com/tu_webhook_real"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Votación Escolar ProA")
        
        # --- MODO KIOSCO PROFESIONAL ---
        self.attributes("-fullscreen", True) # Pantalla completa
        self.bind("<Escape>", lambda e: self.salir_kiosco()) # Solo el Admin sabrá como salir
        
        self.configure(fg_color=COLOR_FONDO)

        ruta_txt = os.path.join(os.path.dirname(__file__), "correos_permitidos.txt")
        self.verificador = VerificadorCorreo(ruta_txt)
        self.db = BaseDeDatos()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both")

        self.frame_actual = None
        self.bind_all("<Control-Shift-A>", self.abrir_admin)
        self.cambiar_pantalla(Inicio)

    def salir_kiosco(self):
        # Seguridad: Solo sale de pantalla completa si pones la clave
        pwd = simpledialog.askstring("Salir", "Contraseña para cerrar Modo Kiosco:", show="*")
        if pwd == ADMIN_PASSWORD:
            self.attributes("-fullscreen", False)
            self.quit()

    def cambiar_pantalla(self, clase_frame, datos=None):
        if self.frame_actual:
            self.frame_actual.destroy()
        if datos:
            self.frame_actual = clase_frame(self.container, self, datos)
        else:
            self.frame_actual = clase_frame(self.container, self)
        self.frame_actual.pack(expand=True, fill="both")

    def abrir_admin(self, event=None):
        pwd = simpledialog.askstring("Acceso Admin", "Ingrese la clave maestra:", show="*")
        if pwd == ADMIN_PASSWORD:
            self.cambiar_pantalla(Admin)
        elif pwd is not None:
            messagebox.showerror("Error", "Clave incorrecta")

class Inicio(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=25, width=600, height=450)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="SISTEMA DE SUFRAGIO DIGITAL", font=("Inter", 20), text_color=COLOR_ACCENTO).pack(pady=(50, 5))
        ctk.CTkLabel(card, text="Elecciones 2026", font=("Inter", 50, "bold")).pack(pady=10)
        ctk.CTkLabel(card, text="ProA - Educación de Vanguardia", font=("Inter", 14), text_color="#64748B").pack()
        
        ctk.CTkButton(card, text="COMENZAR PROCESO", font=("Inter", 20, "bold"), 
                            fg_color=COLOR_ACCENTO, text_color=COLOR_FONDO, height=70, width=350,
                            corner_radius=15,
                            command=lambda: controller.cambiar_pantalla(Formulario)).pack(pady=60)

class Formulario(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=25, width=550, height=450)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Identificación", font=("Inter", 32, "bold")).pack(pady=(50, 10))
        ctk.CTkLabel(card, text="Ingresa tu correo institucional para validar:", font=("Inter", 15), text_color="#94A3B8").pack()

        self.entry = ctk.CTkEntry(card, width=400, height=55, placeholder_text="usuario@escuelasproa.edu.ar",
                                 fg_color=COLOR_FONDO, border_color="#334155", justify="center", font=("Inter", 16))
        self.entry.pack(pady=40)
        
        ctk.CTkButton(card, text="VERIFICAR PADRÓN", font=("Inter", 18, "bold"),
                            fg_color=COLOR_ACCENTO, text_color=COLOR_FONDO,
                            width=250, height=50, command=self.validar).pack()
        
        ctk.CTkButton(card, text="VOLVER", fg_color="transparent", text_color="#94A3B8",
                            command=lambda: controller.cambiar_pantalla(Inicio)).pack(pady=20)

    def validar(self):
        correo = self.entry.get().strip().lower()
        
        # Validación de formato Email (Regex)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            messagebox.showerror("Error de Formato", "Por favor, ingresa un correo electrónico válido.")
            return

        if not self.controller.verificador.correo_permitido(correo):
            messagebox.showerror("No autorizado", "Este correo no figura en el padrón electoral.")
            return
        if self.controller.db.correo_ya_voto(correo):
            messagebox.showwarning("Voto duplicado", "Ya has registrado tu voto anteriormente.")
            return
        
        self.controller.cambiar_pantalla(Votacion, {"correo": correo})

class Votacion(ctk.CTkFrame):
    def __init__(self, parent, controller, datos):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.correo = datos["correo"]

        ctk.CTkLabel(self, text="SELECCIONE SU OPCIÓN", font=("Inter", 35, "bold")).pack(pady=50)
        
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(expand=True)

        # Opciones con mejor diseño
        self.crear_opcion(grid, "LISTA AZUL", "#0072CE", 0, 0)
        self.crear_opcion(grid, "LISTA ROJA", "#D52B1E", 0, 1)
        # Agregamos Voto en Blanco
        self.crear_opcion(grid, "VOTO EN BLANCO", "#475569", 1, 0, columnspan=2)

    def crear_opcion(self, parent, nombre, color, row, col, columnspan=1):
        btn = ctk.CTkButton(parent, text=nombre, fg_color=color, hover_color=color,
                            width=380, height=180, font=("Inter", 28, "bold"),
                            corner_radius=20, border_width=2, border_color="#FFFFFF",
                            command=lambda: self.confirmar_voto(nombre))
        btn.grid(row=row, column=col, columnspan=columnspan, padx=20, pady=20)

    def confirmar_voto(self, lista):
        if messagebox.askyesno("Confirmar", f"¿Confirmas tu voto por {lista}?\nEsta acción no se puede deshacer."):
            if self.controller.db.guardar_voto(self.correo, lista):
                self.controller.cambiar_pantalla(Final)

class Final(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=30, width=600, height=300)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card, text="¡VOTO REGISTRADO! ✅", font=("Inter", 40, "bold"), text_color=COLOR_ACCENTO).pack(expand=True)
        ctk.CTkLabel(card, text="Gracias por participar en la democracia escolar.", font=("Inter", 16)).pack(pady=(0, 40))
        
        self.after(3000, lambda: controller.cambiar_pantalla(Inicio))

class Admin(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        ctk.CTkLabel(self, text="PANEL DE CONTROL", font=("Inter", 35, "bold")).pack(pady=40)
        
        total = self.controller.db.total_votos()
        
        # Dashboard simple
        dash = ctk.CTkFrame(self, fg_color=COLOR_CARD, width=800, height=150)
        dash.pack(pady=10)
        dash.pack_propagate(False)
        
        ctk.CTkLabel(dash, text=f"PARTICIPACIÓN ACTUAL: {total} Votantes", font=("Inter", 22, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        # Botones de Acción
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=30)

        ctk.CTkButton(btns, text="☁️ SINCRONIZAR MAKE.COM", fg_color="#059669", height=60, width=250,
                            font=("Inter", 14, "bold"), command=self.sincronizar_cloud).grid(row=0, column=0, padx=10)
        
        ctk.CTkButton(btns, text="📊 VER GRÁFICO", fg_color="#6366F1", height=60, width=250,
                            font=("Inter", 14, "bold"), command=self.mostrar_grafico).grid(row=0, column=1, padx=10)
        
        ctk.CTkButton(self, text="BORRAR TODOS LOS VOTOS", fg_color="#991B1B", 
                            command=self.reset_db).pack(pady=20)

        ctk.CTkButton(self, text="CERRAR PANEL", fg_color="transparent", border_width=1,
                      command=lambda: controller.cambiar_pantalla(Inicio)).pack(pady=40)

    def reset_db(self):
        if messagebox.askyesno("Peligro", "¡Esto borrará todos los votos de la base de datos!\n¿Continuar?"):
            self.controller.db.borrar_todo_el_padron()
            messagebox.showinfo("Listo", "Base de datos reiniciada.")
            self.controller.cambiar_pantalla(Admin)

    def sincronizar_cloud(self):
        votos = self.controller.db.obtener_votos_detallados()
        if not votos: return messagebox.showwarning("Sin Datos", "No hay votos.")
        
        payload = [{"id_anonimo": v[0], "voto_por": v[1], "fecha": v[2]} for v in votos]
        try:
            response = requests.post(URL_MAKE_WEBHOOK, json=payload, timeout=10)
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "Sincronizado con Google Sheets ✅")
            else:
                messagebox.showerror("Error", "Fallo en la nube.")
        except:
            messagebox.showerror("Error", "Sin conexión a internet.")

    def mostrar_grafico(self):
        stats = self.controller.db.obtener_estadisticas()
        if not stats: return
        etiquetas = [s[0] for s in stats]
        valores = [s[1] for s in stats]
        colores = ['#38BDF8' if "AZUL" in e.upper() else '#F87171' if "ROJA" in e.upper() else '#94A3B8' for e in etiquetas]
        
        plt.figure(figsize=(8,6))
        plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', colors=colores, startangle=140)
        plt.title("Resultados de la Elección")
        plt.show()

if __name__ == "__main__":
    app = App()
    app.mainloop()