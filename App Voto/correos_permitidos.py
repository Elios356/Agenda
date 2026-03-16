import os

class VerificadorCorreo:

    def __init__(self, archivo):
        self.correos = set()

        if not os.path.exists(archivo):
            print(f"⚠️ Error: No se encontró {archivo}")
            return

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                self.correos = {
                    linea.strip().lower()
                    for linea in f
                    if linea.strip()
                }
        except Exception as e:
            print(f"❌ Error al leer correos: {e}")

    def correo_permitido(self, correo):
        return correo.lower() in self.correos