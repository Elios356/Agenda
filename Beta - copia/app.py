from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import random

app = Flask(__name__)
app.secret_key = 'clave_maestra_tiago'

# Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root", # Cambia a "" si en XAMPP no tienes contraseña
    "database": "agenda_pro"
}

# Pool de conexiones para evitar errores de saturación
try:
    pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)
except Exception as e:
    print(f"Error: No se pudo conectar a MySQL. ¿Está prendido XAMPP? -> {e}")

def get_db():
    return pool.get_connection()

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Función para generar colores aleatorios para las materias (usado en el CSS)
def get_color():
    colors = ['#38bdf8', '#fbbf24', '#f87171', '#c084fc', '#4ad395']
    return random.choice(colors)

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['usuario'] = user['usuario']
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = generate_password_hash(request.form['password'])
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)", (usuario, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            flash('El usuario ya existe')
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- RUTAS DE LA AGENDA ---

@app.route('/')
@login_required
def index():
    user_id = session['user_id']
    search = request.args.get('search', '')
    materia_filtro = request.args.get('materia_filtro', '')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Obtener estadísticas
    cursor.execute("SELECT COUNT(*) as count FROM tareas WHERE usuario_id = %s AND estado = 'pendiente'", (user_id,))
    pendientes = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM tareas WHERE usuario_id = %s AND estado = 'completada'", (user_id,))
    completadas = cursor.fetchone()['count']

    # Obtener lista de materias únicas para el filtro
    cursor.execute("SELECT DISTINCT materia FROM tareas WHERE usuario_id = %s", (user_id,))
    materias = [row['materia'] for row in cursor.fetchall()]

    # Consulta principal de tareas
    query = "SELECT * FROM tareas WHERE usuario_id = %s AND estado = 'pendiente'"
    params = [user_id]

    if search:
        query += " AND (tema LIKE %s OR materia LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if materia_filtro:
        query += " AND materia = %s"
        params.append(materia_filtro)

    query += " ORDER BY importante DESC, fecha ASC"
    cursor.execute(query, tuple(params))
    tareas = cursor.fetchall()
    
    # Asignar color visual (opcional, para el diseño)
    for t in tareas:
        t['color'] = get_color()

    conn.close()
    return render_template('index.html', tareas=tareas, usuario=session['usuario'], 
                           pendientes=pendientes, completadas=completadas, materias=materias)

@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if request.method == 'POST':
        materia = request.form['materia']
        tema = request.form['tema']
        fecha = request.form['fecha']
        importante = 1 if request.form.get('importante') else 0
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tareas (usuario_id, materia, tema, fecha, importante) 
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], materia, tema, fecha, importante))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('crear_editar.html', tarea=None)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        materia = request.form['materia']
        tema = request.form['tema']
        fecha = request.form['fecha']
        importante = 1 if request.form.get('importante') else 0
        
        cursor.execute("""
            UPDATE tareas SET materia=%s, tema=%s, fecha=%s, importante=%s 
            WHERE id=%s AND usuario_id=%s
        """, (materia, tema, fecha, importante, id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM tareas WHERE id=%s AND usuario_id=%s", (id, session['user_id']))
    tarea = cursor.fetchone()
    conn.close()
    return render_template('crear_editar.html', tarea=tarea)

@app.route('/completar/<int:id>')
@login_required
def completar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tareas SET estado='completada' WHERE id=%s AND usuario_id=%s", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id=%s AND usuario_id=%s", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html', user={'usuario': session['usuario']})

@app.route('/limpiar')
@login_required
def limpiar():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE usuario_id=%s AND estado='completada'", (session['user_id'],))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/backup')
@login_required
def backup():
    # Simulación de backup o exportar datos
    flash("Función de Backup en desarrollo")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)