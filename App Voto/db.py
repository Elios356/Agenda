import sqlite3
from contextlib import closing

class BaseDeDatos:
    def __init__(self, db_name="votos.db"):
        self.db_name = db_name
        self.crear_tabla()

    def _ejecutar_consulta(self, consulta, parametros=(), fetch=False, fetchone=False):
        try:
            with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
                with closing(conn.cursor()) as cursor:
                    cursor.execute(consulta, parametros)

                    if fetch:
                        return cursor.fetchall()

                    if fetchone:
                        return cursor.fetchone()

                    conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Error DB: {e}")
            return None

    def crear_tabla(self):

        sql = """
        CREATE TABLE IF NOT EXISTS votos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT UNIQUE NOT NULL,
            lista TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        self._ejecutar_consulta(sql)
        self._ejecutar_consulta(
            "CREATE INDEX IF NOT EXISTS idx_correo ON votos(correo)"
        )

    def guardar_voto(self, correo, lista):

        sql = "INSERT INTO votos (correo, lista) VALUES (?, ?)"

        try:
            self._ejecutar_consulta(sql, (correo.strip().lower(), lista))
            return True
        except sqlite3.IntegrityError:
            return False

    def correo_ya_voto(self, correo):

        sql = "SELECT 1 FROM votos WHERE correo = ? LIMIT 1"

        resultado = self._ejecutar_consulta(
            sql,
            (correo.strip().lower(),),
            fetchone=True
        )

        return resultado is not None

    def obtener_estadisticas(self):

        sql = """
        SELECT lista, COUNT(*) 
        FROM votos 
        GROUP BY lista 
        ORDER BY COUNT(*) DESC
        """

        return self._ejecutar_consulta(sql, fetch=True)

    def total_votos(self):

        sql = "SELECT COUNT(*) FROM votos"

        resultado = self._ejecutar_consulta(sql, fetchone=True)

        return resultado[0] if resultado else 0

    def obtener_votos_detallados(self):

        try:

            sql = "SELECT correo, lista, fecha FROM votos"

            return self._ejecutar_consulta(sql, fetch=True)

        except sqlite3.OperationalError:

            sql = "SELECT correo, lista, 'N/A' FROM votos"

            return self._ejecutar_consulta(sql, fetch=True)