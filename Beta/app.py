from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import pooling
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_ultra_pro_agenda'

# Configuración de base de datos
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "agenda_pro"
}

try:
    pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **db_config)
except Exception as e:
    print(f"Error de conexión: {e}")

def get_db():
    return pool.get_connection()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    user_id = session['user_id']
    search = request.args.get('search', '')
    materia_filtro = request.args.get('materia_filtro', '')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Estadísticas
    cursor.execute("SELECT COUNT(*) as c FROM tareas WHERE usuario_id=%s AND estado='pendiente'", (user_id,))
    pendientes = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) as c FROM tareas WHERE usuario_id=%s AND estado='completada'", (user_id,))
    completadas = cursor.fetchone()['c']
    
    # Materias para el filtro
    cursor.execute("SELECT DISTINCT materia FROM tareas WHERE usuario_id=%s", (user_id,))
    materias = [row['materia'] for row in cursor.fetchall()]
    
    # Consulta de tareas
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
    
    conn.close()
    return render_template('index.html', tareas=tareas, pendientes=pendientes, completadas=completadas, materias=materias)

@app.route('/completadas')
@login_required
def ver_completadas():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tareas WHERE usuario_id=%s AND estado='completada' ORDER BY fecha DESC", (session['user_id'],))
    tareas = cursor.fetchall()
    conn.close()
    return render_template('completadas.html', tareas=tareas)

@app.route('/completar/<int:id>')
@login_required
def completar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tareas SET estado='completada' WHERE id=%s AND usuario_id=%s", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/restaurar/<int:id>')
@login_required
def restaurar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tareas SET estado='pendiente' WHERE id=%s AND usuario_id=%s", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_completadas'))

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id=%s AND usuario_id=%s", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('index'))

@app.route('/limpiar')
@login_required
def limpiar():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE usuario_id=%s AND estado='completada'", (session['user_id'],))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_completadas'))

@app.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if request.method == 'POST':
        materia = request.form['materia']
        tema = request.form['tema']
        fecha = request.form['fecha']
        imp = 1 if request.form.get('importante') else 0
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tareas (usuario_id, materia, tema, fecha, importante) VALUES (%s,%s,%s,%s,%s)",
                       (session['user_id'], materia, tema, fecha, imp))
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
        materia, tema, fecha = request.form['materia'], request.form['tema'], request.form['fecha']
        imp = 1 if request.form.get('importante') else 0
        cursor.execute("UPDATE tareas SET materia=%s, tema=%s, fecha=%s, importante=%s WHERE id=%s AND usuario_id=%s",
                       (materia, tema, fecha, imp, id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM tareas WHERE id=%s AND usuario_id=%s", (id, session['user_id']))
    tarea = cursor.fetchone()
    conn.close()
    return render_template('crear_editar.html', tarea=tarea)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['usuario'], request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (u,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], p):
            session['user_id'], session['usuario'] = user['id'], user['usuario']
            return redirect(url_for('index'))
        flash('Credenciales Incorrectas')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        u, p = request.form['usuario'], generate_password_hash(request.form['password'])
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (%s, %s)", (u, p))
            conn.commit()
            return redirect(url_for('login'))
        except: flash('El usuario ya existe')
        finally: conn.close()
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html', user={'usuario': session['usuario']})

if __name__ == '__main__':
    app.run(debug=True, port=5000)