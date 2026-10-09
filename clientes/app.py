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
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT * FROM clientes
    WHERE id = %s
    """

    cursor.execute(sql, (id,))
    clienteEncontrado = cursor.fetchone()

    cursor.close()
    conexion.close()

    if clienteEncontrado is None:
        return jsonify({
            "mensaje": "Cliente no encontrado"
        }), 404

    respuesta = requests.get(
        f"{url_hoteles}/hoteles/{clienteEncontrado['hotel_id']}"
    )

    if respuesta.status_code != 200:
        return jsonify({
            "mensaje": "Hotel no encontrado"
        }), 404

    hotel = respuesta.json()

    return jsonify({
        "cliente": clienteEncontrado["nombre"],
        "hotel": hotel["hotel"],
        "ciudad": hotel["ciudad"],
        "direccion": hotel["direccion"]
    })


app.run(host="0.0.0.0", port=5000)