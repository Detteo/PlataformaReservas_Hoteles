from flask import Flask, jsonify, request
import requests, os
from database import conectar

app = Flask(__name__)

url_hoteles = os.getenv("URL_HOTELES")


@app.route("/clientes", methods=["GET"])
def listar():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT * FROM clientes
    """

    cursor.execute(sql)
    clientes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(clientes)


@app.route("/clientes/<int:id>")
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT * FROM clientes  
    WHERE id = %s
    """

    cursor.execute(sql, (id,))
    cliente = cursor.fetchone()

    cursor.close()
    conexion.close()

    if cliente is None:
        return jsonify({
            "mensaje": "Cliente no encontrado"
        }), 404
    else:
        return jsonify(cliente)


@app.route("/clientes", methods=["POST"])
def crear():
    nuevo_cliente = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    INSERT INTO clientes
    (nombre, hotel_id)
    VALUES (%s, %s)
    """

    valores = (
        nuevo_cliente["nombre"],
        nuevo_cliente["hotel_id"]
    )

    cursor.execute(sql, valores)
    conexion.commit()

    nuevo_id = cursor.lastrowid

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Cliente creado",
        "id": nuevo_id
    }), 201


@app.route("/clientes/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    DELETE FROM clientes
    WHERE id = %s
    """

    cursor.execute(sql, (id,))
    filas_afectadas = cursor.rowcount

    conexion.commit()

    cursor.close()
    conexion.close()

    if filas_afectadas == 0:
        return jsonify({
            "mensaje": "Cliente no encontrado"
        }), 404
    else:
        return jsonify({
            "mensaje": "Cliente eliminado"
        })


# Endpoint PUT
@app.route("/clientes/<int:id>", methods=["PUT"])
def actualizar(id):
    datos_actualizados = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    UPDATE clientes
    SET nombre = %s,
        hotel_id = %s
    WHERE id = %s
    """

    valores = (
        datos_actualizados["nombre"],
        datos_actualizados["hotel_id"],
        id
    )

    cursor.execute(sql, valores)

    if cursor.rowcount == 0:
        cursor.close()
        conexion.close()

        return jsonify({
            "mensaje": "Cliente no encontrado"
        }), 404

    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Cliente actualizado"
    })


@app.route("/clientes/<int:id>/detalle")
def detalle(id):
    tiempo_maximo = float(os.getenv("CLIENTES_TIMEOUT", "4"))
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM clientes WHERE id = %s", (id,)
        )
    cliente = cursor.fetchone()
    cursor.close()
    conexion.close()
    if cliente is None:
        return jsonify({ "mensaje": "Cliente no encontrado"}), 404
    hoteles_id = cliente["hotel_id"]
    url = (os.getenv("URL_HOTELES") + "/hoteles/" + str(hoteles_id))
    try:
        respuesta = requests.get(url, timeout=tiempo_maximo)
        hoteles = respuesta.json()
        return jsonify({
            "cliente": cliente["nombre"],
            "hotel": hoteles["hotel"],
            "ciudad": hoteles["ciudad"],
            "direccion": hoteles["direccion"]
        }), 200
    except requests.exceptions.ConnectionError:
        return jsonify({"mensaje": "Servicio de hoteles no disponible"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"mensaje": "Usuarios tardo demasiado en responder"}), 504
    if respuesta.status_code == 404:
        return jsonify({"mensaje": "Hotel no encontrado"}), 404 


app.run(host="0.0.0.0", port=5000)