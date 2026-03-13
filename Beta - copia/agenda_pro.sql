CREATE DATABASE IF NOT EXISTS agenda_pro;
USE agenda_pro;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tareas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    materia VARCHAR(100) NOT NULL,
    tema VARCHAR(255) NOT NULL,
    fecha DATE NOT NULL,
    importante TINYINT(1) DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'pendiente',

    INDEX idx_usuario (usuario_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha (fecha),

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);