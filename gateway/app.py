from flask import Flask, jsonify, Response, request
import os
import requests

app = Flask(__name__)
URL_CLIENTES = os.getenv("URL_CLIENTES", "http://clientes:5000")
URL_HOTELES = os.getenv("URL_HOTELES", "http://hoteles:5000")

def reenviar(metodo, url):
    try:
        respuesta = requests.request(
            metodo,
            url,
            params=request.args,
            json=request.get_json(silent=True),
            timeout=5
        )
        return Response(
            respuesta.content,
            status=respuesta.status_code,
            content_type=respuesta.headers.get("Content-Type", "application/json")
        )
    except requests.exceptions.Timeout:
        return jsonify({
            "mensaje": "El servicio destino tardo demasiado"
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            "mensaje": "No fue posible conectar con el servicio destino"
        }), 503

@app.route("/clientes", methods=["GET", "POST"])
def ruta_clientes():
    return reenviar(request.method, URL_CLIENTES + "/clientes")

@app.route("/clientes/<path:ruta>", methods=["GET", "DELETE"])
def ruta_clientes_detalle(ruta):
    return reenviar(request.method, URL_CLIENTES + "/clientes/" + ruta)

@app.route("/hoteles/<int:id>", methods=["GET"])
def ruta_hoteles(id):
    return reenviar(request.method, URL_HOTELES + "/hoteles/" + str(id))

app.run(host="0.0.0.0", port=5000)  
