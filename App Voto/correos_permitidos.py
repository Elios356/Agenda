import os

class VerificadorCorreo:

    def __init__(self, archivo):
        self.correos = set()

        if os.path.exists(archivo):
            with open(archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    correo = linea.strip().lower()
                    if correo:
                        self.correos.add(correo)
        else:
            print("No se encontró el archivo de correos permitidos")

    def correo_permitido(self, correo):
        return correo.lower() in self.correos