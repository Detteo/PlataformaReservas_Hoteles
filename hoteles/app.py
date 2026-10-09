from flask import Flask, jsonify, request
from database import conectar

app = Flask(__name__)


@app.route("/hoteles", methods=["GET"])
def listar():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT * FROM hoteles
    """

    cursor.execute(sql)
    hoteles = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(hoteles)


@app.route("/hoteles/<int:id>")
def buscar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT * FROM hoteles
    WHERE id = %s
    """

    cursor.execute(sql, (id,))
    hotel = cursor.fetchone()

    cursor.close()
    conexion.close()

    if hotel is None:
        return jsonify({
            "mensaje": "Hotel no encontrado"
        }), 404
    else:
        return jsonify(hotel)


@app.route("/hoteles", methods=["POST"])
def crear():
    nuevo_hotel = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    INSERT INTO hoteles
    (hotel, ciudad, direccion)
    VALUES (%s, %s, %s)
    """

    valores = (
        nuevo_hotel["hotel"],
        nuevo_hotel["ciudad"],
        nuevo_hotel["direccion"]
    )

    cursor.execute(sql, valores)
    conexion.commit()

    nuevo_id = cursor.lastrowid

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Hotel creado",
        "id": nuevo_id
    }), 201


@app.route("/hoteles/<int:id>", methods=["DELETE"])
def eliminar(id):
    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    DELETE FROM hoteles
    WHERE id = %s
    """

    cursor.execute(sql, (id,))
    filas_afectadas = cursor.rowcount

    conexion.commit()

    cursor.close()
    conexion.close()

    if filas_afectadas == 0:
        return jsonify({
            "mensaje": "Hotel no encontrado"
        }), 404
    else:
        return jsonify({
            "mensaje": "Hotel eliminado"
        })


# Endpoint PUT
@app.route("/hoteles/<int:id>", methods=["PUT"])
def actualizar(id):
    datos_actualizados = request.get_json()

    conexion = conectar()
    cursor = conexion.cursor()

    sql = """
    UPDATE hoteles
    SET hotel = %s,
        ciudad = %s,
        direccion = %s
    WHERE id = %s
    """

    valores = (
        datos_actualizados["hotel"],
        datos_actualizados["ciudad"],
        datos_actualizados["direccion"],
        id
    )

    cursor.execute(sql, valores)

    if cursor.rowcount == 0:
        cursor.close()
        conexion.close()

        return jsonify({
            "mensaje": "Hotel no encontrado"
        }), 404

    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({
        "mensaje": "Hotel actualizado"
    })


app.run(host="0.0.0.0", port=5000)