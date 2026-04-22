import cv2
import base64
import numpy as np
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import deque

from deepface import DeepFace

from database.db import crear_tabla, insertar_usuario, obtener_usuarios

# =========================
# APP INIT
# =========================
app = Flask(__name__)
CORS(app)

crear_tabla()

# =========================
# MEMORIA
# =========================
usuarios_memoria = []
cola_ingresos = deque()

# =========================
# UTILIDAD
# =========================
def decode_image(base64_img):
    img_data = base64.b64decode(base64_img.split(",")[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "SmartAccess funcionando 🔥"

# =========================
# REGISTRO (ELKIN FIJO)
# =========================
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    data = request.json
    imagen = data["imagen"]

    img = decode_image(imagen)

    nombre = "Elkin"

    ruta = f"backend/imagenes/{nombre}.jpg"
    os.makedirs("backend/imagenes", exist_ok=True)
    cv2.imwrite(ruta, img)

    insertar_usuario(nombre)
    usuarios_memoria.append(nombre)
    cola_ingresos.append(nombre)

    return jsonify({"mensaje": "Usuario Elkin registrado"})

# =========================
# RECONOCIMIENTO
# =========================
@app.route("/reconocer", methods=["POST"])
def reconocer():
    data = request.json
    imagen = data["imagen"]

    img = decode_image(imagen)

    ruta = "backend/imagenes/Elkin.jpg"

    try:
        result = DeepFace.verify(img, ruta, enforce_detection=False)

        if result["verified"]:
            return jsonify({"mensaje": "Acceso permitido: Elkin 🔓"})
    except:
        pass

    return jsonify({"mensaje": "Acceso denegado ❌"})

# =========================
# USUARIOS BD
# =========================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = obtener_usuarios()

    return jsonify([
        {"id": u[0], "nombre": u[1]} for u in usuarios
    ])

# =========================
# MEMORIA
# =========================
@app.route("/memoria", methods=["GET"])
def ver_memoria():
    return jsonify(usuarios_memoria)

@app.route("/cola", methods=["GET"])
def ver_cola():
    return jsonify(list(cola_ingresos))

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)