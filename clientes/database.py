import mysql.connector
import os
import time

def conectar():
    for intento in range(10):
        try:
            conexion = mysql.connector.connect(
                host=os.getenv("DB_HOST_CLIENTES"),
                port=int(os.getenv("DB_PORT_CLIENTES", 3306)),
                user=os.getenv("DB_USER_CLIENTES"),
                password=os.getenv("DB_PASSWORD_CLIENTES"),
                database=os.getenv("DB_NAME_CLIENTES")
            )

            print("Conexión a MySQL exitosa")
            return conexion

        except mysql.connector.Error as error:
            print(f"Intento {intento + 1}/10: la base de datos aún no está disponible")
            print("Error:", error)
            time.sleep(3)

    print("No fue posible conectarse a MySQL")
    return None