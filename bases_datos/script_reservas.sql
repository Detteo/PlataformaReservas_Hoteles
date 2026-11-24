CREATE DATABASE IF NOT EXISTS reservas;
USE reservas;

CREATE TABLE IF NOT EXISTS reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    hotel_id INT NOT NULL,
    fecha_entrada DATE NOT NULL,
    fecha_salida DATE NOT NULL,
    estado VARCHAR(30) DEFAULT 'CONFIRMADA'
);

SHOW TABLES;