import cv2
import base64
import numpy as np
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from deepface import DeepFace
from database.db import insertar_usuario, obtener_usuarios

app = Flask(__name__)
CORS(app)

# =========================
# 🔧 DECODIFICAR IMAGEN
# =========================
def decode_image(base64_img):
    img_data = base64.b64decode(base64_img.split(",")[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return "SmartAccess funcionando 🔥"


# =========================
# ➕ REGISTRO (1 IMAGEN)
# =========================
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    data = request.json
    nombre = data.get("nombre")
    imagen = data.get("imagen")

    if not nombre or not imagen:
        return jsonify({"error": "Nombre e imagen requeridos"}), 400

    # convertir imagen
    img = decode_image(imagen)

    # 🔥 mejorar velocidad (reducir tamaño)
    img = cv2.resize(img, (300, 300))

    # carpeta
    os.makedirs("backend/imagenes", exist_ok=True)

    ruta = f"backend/imagenes/{nombre}.jpg"
    cv2.imwrite(ruta, img)

    # guardar en DB
    insertar_usuario(nombre, ruta)

    return jsonify({
        "mensaje": f"Usuario {nombre} registrado correctamente"
    })


# =========================
# 🔍 RECONOCIMIENTO RÁPIDO
# =========================
@app.route("/reconocer", methods=["POST"])
def reconocer():
    data = request.json
    imagen = data.get("imagen")

    if not imagen:
        return jsonify({"error": "Imagen requerida"}), 400

    img = decode_image(imagen)

    # 🔥 reducir tamaño → más rápido
    img = cv2.resize(img, (300, 300))

    usuarios = obtener_usuarios()

    mejor_usuario = None
    mejor_distancia = 1

    for u in usuarios:
        nombre = u[1]
        ruta = u[2]

        try:
            result = DeepFace.verify(
                img,
                ruta,
                model_name="Facenet",   # ⚡ rápido
                enforce_detection=True
            )

            distancia = result["distance"]

            # quedarse con el mejor match
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_usuario = nombre

        except:
            continue

    # 🎯 VALIDACIÓN (ajusta si quieres)
    if mejor_usuario and mejor_distancia < 0.38:
        return jsonify({
            "mensaje": f"Acceso permitido: {mejor_usuario} 🔓",
            "confianza": float(mejor_distancia)
        })

    return jsonify({
        "mensaje": "Acceso denegado ❌"
    })


# =========================
# 📋 DEBUG
# =========================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = obtener_usuarios()

    return jsonify([
        {"id": u[0], "nombre": u[1], "imagen": u[2]}
        for u in usuarios
    ])


# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)