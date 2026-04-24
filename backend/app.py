import cv2
import base64
import numpy as np
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from deepface import DeepFace # type: ignore
from database.db import insertar_usuario, obtener_usuarios

app = Flask(__name__)
CORS(app)

RUTA_IMAGENES = "backend/imagenes"
os.makedirs(RUTA_IMAGENES, exist_ok=True)


# =========================
# 🔧 DECODIFICAR IMAGEN
# =========================
def decode_image(base64_img):
    try:
        img_data = base64.b64decode(base64_img.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print("❌ Error decodificando:", e)
        return None


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return "SmartAccess funcionando 🔥"


# =========================
# ➕ REGISTRO
# =========================
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    data = request.json

    nombre = data.get("nombre")
    imagen = data.get("imagen")

    if not nombre or not imagen:
        return jsonify({"error": "Nombre e imagen requeridos"}), 400

    img = decode_image(imagen)

    if img is None:
        return jsonify({"error": "Imagen inválida"}), 400

    # ❌ NO resize (clave)
    nombre_archivo = f"{nombre.lower().replace(' ', '_')}.jpg"
    ruta = os.path.join(RUTA_IMAGENES, nombre_archivo)

    cv2.imwrite(ruta, img)

    insertar_usuario(nombre, ruta)

    return jsonify({"mensaje": f"{nombre} registrado ✅"})


# =========================
# 🔍 RECONOCER
# =========================
@app.route("/reconocer", methods=["POST"])
def reconocer():
    data = request.json
    imagen = data.get("imagen")

    img = decode_image(imagen)

    if img is None:
        return jsonify({"error": "Imagen inválida"}), 400

    usuarios = obtener_usuarios()

    if not usuarios:
        return jsonify({"mensaje": "No hay usuarios registrados"})

    mejor_usuario = None
    mejor_distancia = 1

    for u in usuarios:
        nombre = u["nombre"]
        ruta = u["imagen"]

        if not os.path.exists(ruta):
            print("⚠️ Imagen no encontrada:", ruta)
            continue

        try:
            result = DeepFace.verify(
                img,
                ruta,
                model_name="Facenet",
                enforce_detection=False
            )

            distancia = result["distance"]

            print(f"Comparando con {nombre} → {distancia}")

            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_usuario = nombre

        except Exception as e:
            print("Error:", e)

    # 🔥 UMBRAL MÁS RELAJADO
    if mejor_usuario and mejor_distancia < 0.6:
        return jsonify({
            "mensaje": f"Acceso permitido: {mejor_usuario} 🔓",
            "confianza": float(mejor_distancia)
        })

    return jsonify({"mensaje": "Acceso denegado ❌"})


# =========================
# 📋 LISTAR (CORREGIDO)
# =========================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = obtener_usuarios()

    return jsonify([
        {
            "id": u["id"],
            "nombre": u["nombre"],
            "imagen": u["imagen"]
        }
        for u in usuarios
    ])


# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)