CREATE DATABASE sistema_notas;
USE sistema_notas;

CREATE TABLE alumnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    edad INT,
    calificacion FLOAT,
    estado VARCHAR(20)
);