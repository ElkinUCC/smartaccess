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

# Ruta centralizada (mejor práctica)
RUTA_IMAGENES = "backend/imagenes"
os.makedirs(RUTA_IMAGENES, exist_ok=True)


# =========================
# 🔧 DECODIFICAR IMAGEN
# =========================
def decode_image(base64_img):
    """
    Convierte una imagen en base64 a formato OpenCV (numpy array)
    """
    try:
        img_data = base64.b64decode(base64_img.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("No se pudo decodificar la imagen")

        return img

    except Exception as e:
        print("Error decodificando imagen:", e)
        return None


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

    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    nombre = data.get("nombre")
    imagen = data.get("imagen")

    if not nombre or not imagen:
        return jsonify({"error": "Nombre e imagen requeridos"}), 400

    # 🔹 decodificar imagen
    img = decode_image(imagen)

    if img is None:
        return jsonify({"error": "Imagen inválida"}), 400

    # 🔥 reducir tamaño → mejora rendimiento
    img = cv2.resize(img, (300, 300))

    # 🔹 evitar nombres peligrosos (seguridad básica)
    nombre_archivo = f"{nombre.replace(' ', '_').lower()}.jpg"
    ruta = os.path.join(RUTA_IMAGENES, nombre_archivo)

    # 🔹 guardar imagen
    cv2.imwrite(ruta, img)

    # 🔹 guardar en base de datos
    insertar_usuario(nombre, ruta)

    return jsonify({
        "mensaje": f"Usuario {nombre} registrado correctamente"
    })


# =========================
# 🔍 RECONOCIMIENTO
# =========================
@app.route("/reconocer", methods=["POST"])
def reconocer():
    data = request.json

    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    imagen = data.get("imagen")

    if not imagen:
        return jsonify({"error": "Imagen requerida"}), 400

    # 🔹 decodificar imagen
    img = decode_image(imagen)

    if img is None:
        return jsonify({"error": "Imagen inválida"}), 400

    # 🔥 optimización
    img = cv2.resize(img, (300, 300))

    usuarios = obtener_usuarios()

    if not usuarios:
        return jsonify({"error": "No hay usuarios registrados"}), 404

    mejor_usuario = None
    mejor_distancia = float("inf")  # 🔥 mejor que poner 1

    # 🔁 RECORRIDO (esto es como una lista)
    for u in usuarios:
        nombre = u[1]
        ruta = u[2]

        try:
            result = DeepFace.verify(
                img,
                ruta,
                model_name="Facenet",
                enforce_detection=True
            )

            distancia = result["distance"]

            # 🔹 nos quedamos con el mejor match
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_usuario = nombre

        except Exception as e:
            print(f"Error comparando con {nombre}:", e)
            continue

    # 🎯 UMBRAL DE DECISIÓN
    if mejor_usuario and mejor_distancia < 0.38:
        return jsonify({
            "mensaje": f"Acceso permitido: {mejor_usuario} 🔓",
            "confianza": float(mejor_distancia)
        })

    return jsonify({
        "mensaje": "Acceso denegado ❌"
    })


# =========================
# 📋 LISTAR USUARIOS
# =========================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = obtener_usuarios()

    return jsonify([
        {
            "id": u[0],
            "nombre": u[1],
            "imagen": u[2]
        }
        for u in usuarios
    ])


# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)