import cv2
import base64
import numpy as np
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from deepface import DeepFace
from database.db import insertar_usuario, obtener_usuarios

# =========================
# APP INIT
# =========================
app = Flask(__name__)
CORS(app)

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
# REGISTRAR USUARIO (MULTI)
# =========================
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    data = request.json
    nombre = data.get("nombre")
    imagen = data.get("imagen")

    if not nombre or not imagen:
        return jsonify({"error": "Nombre e imagen requeridos"}), 400

    img = decode_image(imagen)

    # crear carpeta si no existe
    os.makedirs("backend/imagenes", exist_ok=True)

    # guardar imagen
    ruta = f"backend/imagenes/{nombre}.jpg"
    cv2.imwrite(ruta, img)

    # guardar en MySQL
    insertar_usuario(nombre, ruta)

    return jsonify({"mensaje": f"Usuario {nombre} registrado correctamente"})

# =========================
# RECONOCIMIENTO MULTIUSUARIO
# =========================
@app.route("/reconocer", methods=["POST"])
def reconocer():
    data = request.json
    imagen = data.get("imagen")

    if not imagen:
        return jsonify({"error": "Imagen requerida"}), 400

    img = decode_image(imagen)

    usuarios = obtener_usuarios()

    for u in usuarios:
        nombre = u[1]
        ruta = u[2]

        try:
            result = DeepFace.verify(img, ruta, enforce_detection=False)

            if result["verified"]:
                return jsonify({
                    "mensaje": f"Acceso permitido: {nombre} 🔓"
                })

        except:
            continue

    return jsonify({"mensaje": "Acceso denegado ❌"})

# =========================
# LISTAR USUARIOS (DEBUG)
# =========================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = obtener_usuarios()

    return jsonify([
        {"id": u[0], "nombre": u[1], "imagen": u[2]}
        for u in usuarios
    ])

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)