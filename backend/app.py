import cv2
import base64
import numpy as np
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from deepface import DeepFace  # type: ignore
from database.db import insertar_usuario, obtener_usuarios

app = Flask(__name__)
CORS(app)

# 📁 Carpeta imágenes
RUTA_IMAGENES = "backend/imagenes"
os.makedirs(RUTA_IMAGENES, exist_ok=True)


# =========================
# 🔧 DECODIFICAR IMAGEN
# =========================
def decode_image(base64_img):
    try:
        if "," not in base64_img:
            raise ValueError("Formato base64 inválido")

        img_data = base64.b64decode(base64_img.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("No se pudo decodificar")

        return img

    except Exception as e:
        print("❌ Error decodificando imagen:", e)
        return None


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return "SmartAccess funcionando 🔥"


# =========================
# ➕ REGISTRAR USUARIO
# =========================
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400

        nombre = data.get("nombre")
        imagen = data.get("imagen")

        if not nombre or not imagen:
            return jsonify({"error": "Nombre e imagen requeridos"}), 400

        img = decode_image(imagen)

        if img is None:
            return jsonify({"error": "Imagen inválida"}), 400

        # 🔥 optimización
        img = cv2.resize(img, (300, 300))

        nombre_archivo = f"{nombre.strip().replace(' ', '_').lower()}.jpg"
        ruta = os.path.join(RUTA_IMAGENES, nombre_archivo)

        cv2.imwrite(ruta, img)

        # 🔥 guardar en BD (protegido)
        try:
            insertar_usuario(nombre, ruta)
        except Exception as e:
            print("⚠️ Error DB:", e)
            return jsonify({
                "mensaje": f"{nombre} guardado en imagen pero DB falló"
            })

        return jsonify({
            "mensaje": f"Usuario {nombre} registrado correctamente ✅"
        })

    except Exception as e:
        print("❌ Error en registro:", e)
        return jsonify({"error": "Error interno"}), 500


# =========================
# 🔍 RECONOCER
# =========================
@app.route("/reconocer", methods=["POST"])
def reconocer():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400

        imagen = data.get("imagen")

        if not imagen:
            return jsonify({"error": "Imagen requerida"}), 400

        img = decode_image(imagen)

        if img is None:
            return jsonify({"error": "Imagen inválida"}), 400

        img = cv2.resize(img, (300, 300))

        # 🔥 intentar obtener usuarios (si DB falla → no rompe todo)
        try:
            usuarios = obtener_usuarios()
        except Exception as e:
            print("⚠️ Error DB:", e)
            return jsonify({
                "mensaje": "Error de base de datos ❌"
            }), 500

        if not usuarios:
            return jsonify({
                "mensaje": "No hay usuarios registrados"
            }), 404

        mejor_usuario = None
        mejor_distancia = float("inf")

        for u in usuarios:
            nombre = u["nombre"]
            ruta = u["imagen"]

            if not os.path.exists(ruta):
                continue

            try:
                result = DeepFace.verify(
                    img,
                    ruta,
                    model_name="Facenet",
                    enforce_detection=False  # 🔥 clave para que no falle
                )

                distancia = result["distance"]

                if distancia < mejor_distancia:
                    mejor_distancia = distancia
                    mejor_usuario = nombre

            except Exception as e:
                print(f"⚠️ Error con {nombre}:", e)
                continue

        # 🎯 UMBRAL (ajustable)
        if mejor_usuario and mejor_distancia < 0.45:
            return jsonify({
                "mensaje": f"Acceso permitido: {mejor_usuario} 🔓",
                "confianza": float(mejor_distancia)
            })

        return jsonify({
            "mensaje": "Acceso denegado ❌"
        })

    except Exception as e:
        print("❌ Error en reconocimiento:", e)
        return jsonify({"error": "Error interno"}), 500


# =========================
# 📋 LISTAR
# =========================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        usuarios = obtener_usuarios()

        return jsonify([
            {
                "id": u[0],
                "nombre": u[1],
                "imagen": u[2]
            }
            for u in usuarios
        ])

    except Exception as e:
        print("❌ Error listando:", e)
        return jsonify([])


# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)