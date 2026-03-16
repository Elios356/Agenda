from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# CONFIGURACIÓN DE BASE DE DATOS
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root", # <-- ¡PONÉ TU CONTRASEÑA DE MYSQL AQUÍ!
        database="sistema_notas"
    )

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Traemos todos los alumnos
    cursor.execute("SELECT * FROM alumnos ORDER BY id DESC")
    alumnos = cursor.fetchall()
    
    # Cálculos para el resumen y el gráfico
    aprobados = sum(1 for a in alumnos if a['estado'] == 'Aprobado')
    desaprobados = sum(1 for a in alumnos if a['estado'] == 'Desaprobado')
    
    # Cálculo del promedio general
    total_notas = sum(a['calificacion'] for a in alumnos)
    promedio = round(total_notas / len(alumnos), 2) if alumnos else 0
    
    cursor.close()
    db.close()
    return render_template('index.html', alumnos=alumnos, ap=aprobados, des=desaprobados, prom=promedio)

@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    edad = int(request.form['edad'])
    nota = float(request.form['nota'])
    estado = "Aprobado" if nota >= 6 else "Desaprobado"
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO alumnos (nombre, edad, calificacion, estado) VALUES (%s, %s, %s, %s)", 
                   (nombre, edad, nota, estado))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM alumnos WHERE id = %s", (id,))
    db.commit()
    db.close()
    return redirect(url_for('index'))

@app.route('/editar', methods=['POST'])
def editar():
    id = request.form['id']
    nueva_nota = float(request.form['nota'])
    nuevo_estado = "Aprobado" if nueva_nota >= 6 else "Desaprobado"
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE alumnos SET calificacion = %s, estado = %s WHERE id = %s", 
                   (nueva_nota, nuevo_estado, id))
    db.commit()
    db.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)