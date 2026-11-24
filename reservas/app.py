from flask import Flask, jsonify, request
import requests
import os
import pybreaker
from database import conectar

app = Flask(__name__)

url_clientes = os.getenv("URL_CLIENTES", "http://clientes:5000")
url_hoteles = os.getenv("URL_HOTELES", "http://hoteles:5000")

timeout_clientes = float(os.getenv("RESERVAS_TIMEOUT_CLIENTES", os.getenv("CLIENTES_TIMEOUT", "4")))
timeout_hoteles = float(os.getenv("RESERVAS_TIMEOUT_HOTELES", os.getenv("CLIENTES_TIMEOUT", "4")))

max_fallos = int(os.getenv("CB_MAX_FALLOS", "3"))
tiempo_recuperacion = int(os.getenv("CB_RECUPERACION", "30"))

circuito_clientes = pybreaker.CircuitBreaker(
    fail_max=max_fallos,
    reset_timeout=tiempo_recuperacion,
    throw_new_error_on_trip=False,
)

circuito_hoteles = pybreaker.CircuitBreaker(
    fail_max=max_fallos,
    reset_timeout=tiempo_recuperacion,
    throw_new_error_on_trip=False,
)


def consultar_servicio_externo(url, timeout, circuito, nombre_servicio):
    try:
        with circuito.calling():
            respuesta = requests.get(url, timeout=timeout)
            if respuesta.status_code >= 500:
                respuesta.raise_for_status()
            return respuesta, None
    except pybreaker.CircuitBreakerError:
        return None, (jsonify({"mensaje": f"Circuito abierto: servicio de {nombre_servicio} no disponible"}), 503)
    except requests.exceptions.Timeout:
        return None, (jsonify({"mensaje": f"El servicio de {nombre_servicio} tardó demasiado en responder"}), 504)
    except requests.exceptions.ConnectionError:
        return None, (jsonify({"mensaje": f"Servicio de {nombre_servicio} no disponible"}), 503)
    except requests.exceptions.HTTPError:
        return None, (jsonify({"mensaje": f"Error en el servidor de {nombre_servicio}"}), 502)


@app.route("/reservas", methods=["GET"])
def listar():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reservas")
    reservas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(reservas), 200


@app.route("/reservas/<int:id>", methods=["GET"])
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reservas WHERE id = %s", (id,))
    reserva = cursor.fetchone()

    cursor.close()
    conexion.close()

    if reserva is None:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    return jsonify(reserva), 200


@app.route("/reservas", methods=["POST"])
def crear():
    datos = request.get_json() or {}
    for campo in ("cliente_id", "hotel_id", "fecha_entrada", "fecha_salida"):
        if campo not in datos:
            return jsonify({"mensaje": f"Falta el campo obligatorio: {campo}"}), 400

    cliente_id = datos["cliente_id"]
    hotel_id = datos["hotel_id"]

    resp_cliente, error_cliente = consultar_servicio_externo(
        f"{url_clientes}/clientes/{cliente_id}",
        timeout_clientes,
        circuito_clientes,
        "clientes",
    )
    if error_cliente:
        return error_cliente
    if resp_cliente.status_code == 404:
        return jsonify({"mensaje": "Cliente no encontrado"}), 404
    if resp_cliente.status_code != 200:
        return jsonify({"mensaje": "Respuesta inesperada del servicio de clientes"}), 502

    resp_hotel, error_hotel = consultar_servicio_externo(
        f"{url_hoteles}/hoteles/{hotel_id}",
        timeout_hoteles,
        circuito_hoteles,
        "hoteles",
    )
    if error_hotel:
        return error_hotel
    if resp_hotel.status_code == 404:
        return jsonify({"mensaje": "Hotel no encontrado"}), 404
    if resp_hotel.status_code != 200:
        return jsonify({"mensaje": "Respuesta inesperada del servicio de hoteles"}), 502

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO reservas (cliente_id, hotel_id, fecha_entrada, fecha_salida, estado)
    VALUES (%s, %s, %s, %s, %s)
    """
    valores = (
        cliente_id,
        hotel_id,
        datos["fecha_entrada"],
        datos["fecha_salida"],
        datos.get("estado", "CONFIRMADA"),
    )

    cursor.execute(sql, valores)
    conexion.commit()
    nuevo_id = cursor.lastrowid

    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Reserva creada", "id": nuevo_id}), 201


@app.route("/reservas/<int:id>", methods=["PUT"])
def actualizar(id):
    datos = request.get_json() or {}

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservas WHERE id = %s", (id,))
    actual = cursor.fetchone()

    if actual is None:
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    cliente_id = datos.get("cliente_id", actual["cliente_id"])
    hotel_id = datos.get("hotel_id", actual["hotel_id"])
    fecha_entrada = datos.get("fecha_entrada", actual["fecha_entrada"])
    fecha_salida = datos.get("fecha_salida", actual["fecha_salida"])
    estado = datos.get("estado", actual["estado"])

    sql = """
    UPDATE reservas
    SET cliente_id = %s,
        hotel_id = %s,
        fecha_entrada = %s,
        fecha_salida = %s,
        estado = %s
    WHERE id = %s
    """
    cursor.execute(sql, (cliente_id, hotel_id, fecha_entrada, fecha_salida, estado, id))
    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Reserva actualizada"}), 200


@app.route("/reservas/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM reservas WHERE id = %s", (id,))
    filas = cursor.rowcount
    conexion.commit()

    cursor.close()
    conexion.close()

    if filas == 0:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    return jsonify({"mensaje": "Reserva eliminada"}), 200


@app.route("/reservas/<int:id>/detalle", methods=["GET"])
def detalle(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reservas WHERE id = %s", (id,))
    reserva = cursor.fetchone()
    cursor.close()
    conexion.close()

    if reserva is None:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    resp_cliente, error_cliente = consultar_servicio_externo(
        f"{url_clientes}/clientes/{reserva['cliente_id']}",
        timeout_clientes,
        circuito_clientes,
        "clientes",
    )
    if error_cliente:
        return error_cliente
    if resp_cliente.status_code == 404:
        return jsonify({"mensaje": "Cliente asociado no encontrado"}), 404

    resp_hotel, error_hotel = consultar_servicio_externo(
        f"{url_hoteles}/hoteles/{reserva['hotel_id']}",
        timeout_hoteles,
        circuito_hoteles,
        "hoteles",
    )
    if error_hotel:
        return error_hotel
    if resp_hotel.status_code == 404:
        return jsonify({"mensaje": "Hotel asociado no encontrado"}), 404

    cliente = resp_cliente.json()
    hotel = resp_hotel.json()

    return jsonify({
        "reserva_id": reserva["id"],
        "estado": reserva["estado"],
        "fecha_entrada": str(reserva["fecha_entrada"]),
        "fecha_salida": str(reserva["fecha_salida"]),
        "cliente": cliente.get("nombre"),
        "hotel": hotel.get("hotel"),
        "ciudad": hotel.get("ciudad"),
        "direccion": hotel.get("direccion"),
    }), 200


@app.route("/reservas/circuito", methods=["GET"])
def estado_circuito_reservas():
    return jsonify({
        "clientes": {
            "estado": circuito_clientes.current_state.upper(),
            "fallos_consecutivos": circuito_clientes.fail_counter,
            "umbral_fallos": circuito_clientes.fail_max,
            "periodo_recuperacion": circuito_clientes.reset_timeout,
        },
        "hoteles": {
            "estado": circuito_hoteles.current_state.upper(),
            "fallos_consecutivos": circuito_hoteles.fail_counter,
            "umbral_fallos": circuito_hoteles.fail_max,
            "periodo_recuperacion": circuito_hoteles.reset_timeout,
        },
    }), 200


@app.after_request
def agregar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE"
    return response

app.run(host="0.0.0.0", port=5000)