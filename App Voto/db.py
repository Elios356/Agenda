import sqlite3
import hashlib
from contextlib import closing

class BaseDeDatos:
    def __init__(self, db_name="votos.db"):
        self.db_name = db_name
        self.crear_tabla()

    def _generar_hash(self, correo):
        """Convierte el correo en un código anónimo irreversible."""
        return hashlib.sha256(correo.strip().lower().encode()).hexdigest()

    def _ejecutar_consulta(self, consulta, parametros=(), fetch=False, fetchone=False):
        try:
            with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute(consulta, parametros)
                    if fetch: return cursor.fetchall()
                    if fetchone: return cursor.fetchone()
                    conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Error DB: {e}")
            return None

    def crear_tabla(self):
        # La columna correo ahora guardará el HASH para anonimato
        sql = """
        CREATE TABLE IF NOT EXISTS votos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo_hash TEXT UNIQUE NOT NULL,
            lista TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self._ejecutar_consulta(sql)
        self._ejecutar_consulta("CREATE INDEX IF NOT EXISTS idx_hash ON votos(correo_hash)")

    def guardar_voto(self, correo, lista):
        correo_hash = self._generar_hash(correo)
        sql = "INSERT INTO votos (correo_hash, lista) VALUES (?, ?)"
        try:
            # Aquí se guarda el hash, no el correo real
            self._ejecutar_consulta(sql, (correo_hash, lista))
            return True
        except sqlite3.IntegrityError:
            return False

    def correo_ya_voto(self, correo):
        correo_hash = self._generar_hash(correo)
        sql = "SELECT 1 FROM votos WHERE correo_hash = ? LIMIT 1"
        resultado = self._ejecutar_consulta(sql, (correo_hash,), fetchone=True)
        return resultado is not None

    def obtener_estadisticas(self):
        sql = "SELECT lista, COUNT(*) FROM votos GROUP BY lista ORDER BY COUNT(*) DESC"
        return self._ejecutar_consulta(sql, fetch=True)

    def total_votos(self):
        sql = "SELECT COUNT(*) FROM votos"
        resultado = self._ejecutar_consulta(sql, fetchone=True)
        return resultado[0] if resultado else 0

    def obtener_votos_detallados(self):
        # Nota: Por seguridad, aquí enviamos el HASH a la nube, no el correo real.
        sql = "SELECT correo_hash, lista, fecha FROM votos"
        return self._ejecutar_consulta(sql, fetch=True)
        
    def borrar_todo_el_padron(self):
        """Limpieza para nuevas elecciones (Uso exclusivo Admin)"""
        self._ejecutar_consulta("DELETE FROM votos")