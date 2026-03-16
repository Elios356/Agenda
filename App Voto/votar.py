import customtkinter as ctk
import os
import requests
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt

from db import BaseDeDatos
from correos_permitidos import VerificadorCorreo

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
        self.geometry("1000x800")
        self.configure(fg_color=COLOR_FONDO)

        ruta_txt = os.path.join(os.path.dirname(__file__), "correos_permitidos.txt")
        self.verificador = VerificadorCorreo(ruta_txt)
        self.db = BaseDeDatos()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both")

        self.frame_actual = None
        self.bind_all("<Control-Shift-A>", self.abrir_admin)
        self.cambiar_pantalla(Inicio)

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
        # CORRECCIÓN: Dimensiones en el constructor
        card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=25, width=500, height=400)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False) # Evita que el frame se encoja al contenido

        ctk.CTkLabel(card, text="BIENVENIDOS AL SISTEMA", font=("Inter", 20), text_color=COLOR_ACCENTO).pack(pady=(40, 5))
        ctk.CTkLabel(card, text="Elecciones 2026", font=("Inter", 45, "bold")).pack(pady=10)
        ctk.CTkButton(card, text="INGRESAR A VOTAR", font=("Inter", 20, "bold"), 
                            fg_color=COLOR_ACCENTO, text_color=COLOR_FONDO, height=60, width=300,
                            command=lambda: controller.cambiar_pantalla(Formulario)).pack(pady=50)

class Formulario(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # CORRECCIÓN: Dimensiones en el constructor
        card = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=25, width=500, height=400)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Validación de Padrón", font=("Inter", 28, "bold")).pack(pady=(40, 20))
        self.entry = ctk.CTkEntry(card, width=350, height=50, placeholder_text="ejemplo@escuelasproa.edu.ar",
                                 fg_color=COLOR_FONDO, border_color="#334155", justify="center")
        self.entry.pack(pady=30)
        ctk.CTkButton(card, text="VALIDAR E INGRESAR", font=("Inter", 16, "bold"),
                                        fg_color=COLOR_ACCENTO, text_color=COLOR_FONDO,
                                        width=200, height=45, command=self.validar).pack(pady=(0, 40))

    def validar(self):
        correo = self.entry.get().strip().lower()
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

        ctk.CTkLabel(self, text="EMISIÓN DE SUFRAGIO", font=("Inter", 32, "bold")).pack(pady=40)
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(expand=True)

        self.crear_opcion(grid, "LISTA AZUL", "#0072CE", 0, 0)
        self.crear_opcion(grid, "LISTA ROJA", "#D52B1E", 0, 1)
        self.crear_opcion(grid, "Blanco", "#64748B", 1, 0, columnspan=2)

    def crear_opcion(self, parent, nombre, color, row, col, columnspan=1):
        btn = ctk.CTkButton(parent, text=nombre, fg_color=color, hover_color=color,
                            width=350, height=150, font=("Inter", 26, "bold"),
                            corner_radius=20, command=lambda: self.confirmar_voto(nombre))
        btn.grid(row=row, column=col, columnspan=columnspan, padx=15, pady=15)

    def confirmar_voto(self, lista):
        if messagebox.askyesno("Confirmar Selección", f"¿Estás seguro de votar por: {lista}?"):
            if self.controller.db.guardar_voto(self.correo, lista):
                self.controller.cambiar_pantalla(Final)

class Final(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        # CORRECCIÓN: Label centrado usando place sin argumentos inválidos
        lbl = ctk.CTkLabel(self, text="¡VOTO REGISTRADO CON ÉXITO! ✅", 
                           font=("Inter", 38, "bold"), text_color=COLOR_ACCENTO)
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        self.after(3000, lambda: controller.cambiar_pantalla(Inicio))

class Admin(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        ctk.CTkLabel(self, text="PANEL DE ADMINISTRACIÓN", font=("Inter", 32, "bold")).pack(pady=30)
        
        total = self.controller.db.total_votos()
        ctk.CTkLabel(self, text=f"Total de Votos Emitidos: {total}", font=("Inter", 18)).pack(pady=5)
        
        ctk.CTkButton(self, text="☁️ SINCRONIZAR CON GOOGLE SHEETS", 
                                      fg_color="#059669", hover_color="#047857",
                                      font=("Inter", 16, "bold"), height=50,
                                      command=self.sincronizar_cloud).pack(pady=20)
        ctk.CTkButton(self, text="VER GRÁFICO LOCAL", command=self.mostrar_grafico).pack(pady=10)
        ctk.CTkButton(self, text="CERRAR SESIÓN", fg_color="transparent", border_width=1,
                      command=lambda: controller.cambiar_pantalla(Inicio)).pack(pady=30)

    def sincronizar_cloud(self):
        votos = self.controller.db.obtener_votos_detallados()
        if not votos:
            return messagebox.showwarning("Sin Datos", "No hay votos para sincronizar.")
        payload = [{"estudiante": v[0], "voto_por": v[1], "fecha_hora": v[2]} for v in votos]
        try:
            response = requests.post(URL_MAKE_WEBHOOK, json=payload, timeout=10)
            if response.status_code == 200:
                messagebox.showinfo("Éxito", "¡Datos sincronizados con la nube! ☁️")
            else:
                messagebox.showerror("Error", f"Fallo en Make: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar con Make: {e}")

    def mostrar_grafico(self):
        stats = self.controller.db.obtener_estadisticas()
        if not stats: return
        etiquetas = [s[0] for s in stats]
        valores = [s[1] for s in stats]
        colores = []
        for e in etiquetas:
            if "AZUL" in e.upper(): colores.append('#38BDF8')
            elif "ROJA" in e.upper(): colores.append('#F87171')
            else: colores.append('#94A3B8')
            
        plt.figure(figsize=(8,6))
        plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', colors=colores)
        plt.title("Resultados de la Elección")
        plt.show()

if __name__ == "__main__":
    app = App()
    app.mainloop()