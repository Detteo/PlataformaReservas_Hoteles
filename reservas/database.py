import os
import mysql.connector


def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST_RESERVAS", "mysql_reservas"),
        port=int(os.getenv("DB_PORT_RESERVAS", "3306")),
        user=os.getenv("DB_USER_RESERVAS", "root"),
        password=os.getenv("DB_PASSWORD_RESERVAS", "root"),
        database=os.getenv("DB_NAME_RESERVAS", "reservas"),
    )