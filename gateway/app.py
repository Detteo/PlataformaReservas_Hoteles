from flask import Flask, jsonify, Response, request
import os
import requests

app = Flask(__name__)

URL_CLIENTES = os.getenv("URL_CLIENTES", "http://clientes:5000")
URL_HOTELES = os.getenv("URL_HOTELES", "http://hoteles:5000")
URL_RESERVAS = os.getenv("URL_RESERVAS", "http://reservas:5000")
GATEWAY_TIMEOUT = float(os.getenv("GATEWAY_TIMEOUT", "5"))


@app.before_request
def manejar_preflight():
    if request.method == "OPTIONS":
        response = Response("", status=204)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return response


def reenviar(metodo, url):
    try:
        kwargs = {
            "params": request.args,
            "timeout": GATEWAY_TIMEOUT,
        }
        if request.get_json(silent=True) is not None:
            kwargs["json"] = request.get_json(silent=True)

        respuesta = requests.request(metodo, url, **kwargs)
        return Response(
            respuesta.content,
            status=respuesta.status_code,
            content_type=respuesta.headers.get("Content-Type", "application/json"),
        )
    except requests.exceptions.Timeout:
        return jsonify({
            "mensaje": "El servicio destino tardo demasiado"
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            "mensaje": "No fue posible conectar con el servicio destino"
        }), 503


# --- Rutas de Clientes ---
@app.route("/clientes", methods=["GET", "POST"])
def ruta_clientes():
    return reenviar(request.method, f"{URL_CLIENTES}/clientes")


@app.route("/clientes/<path:ruta>", methods=["GET", "PUT", "DELETE"])
def ruta_clientes_subrutas(ruta):
    return reenviar(request.method, f"{URL_CLIENTES}/clientes/{ruta}")


# --- Rutas de Hoteles ---
@app.route("/hoteles", methods=["GET", "POST"])
def ruta_hoteles():
    return reenviar(request.method, f"{URL_HOTELES}/hoteles")


@app.route("/hoteles/<path:ruta>", methods=["GET", "PUT", "DELETE"])
def ruta_hoteles_subrutas(ruta):
    return reenviar(request.method, f"{URL_HOTELES}/hoteles/{ruta}")


# --- Rutas de Reservas ---
@app.route("/reservas", methods=["GET", "POST"])
def ruta_reservas():
    return reenviar(request.method, f"{URL_RESERVAS}/reservas")


@app.route("/reservas/<path:ruta>", methods=["GET", "PUT", "DELETE"])
def ruta_reservas_subrutas(ruta):
    return reenviar(request.method, f"{URL_RESERVAS}/reservas/{ruta}")


@app.after_request
def agregar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response
app.run(host="0.0.0.0", port=5000)