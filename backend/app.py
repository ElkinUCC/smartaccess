import cv2
import base64
import numpy as np
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from deepface import DeepFace # type: ignore
from database.db import insertar_usuario, obtener_usuarios, insertar_log

# 🟡 COLA
from collections import deque

app = Flask(__name__)
CORS(app)

RUTA_IMAGENES = "backend/imagenes"
os.makedirs(RUTA_IMAGENES, exist_ok=True)


# =========================
# 🔧 DECODIFICAR IMAGEN (RECURSION)
# =========================
def decode_image(base64_img, intento=0):
    """
    RECURSION:
    Se reintenta decodificar la imagen hasta 2 veces si falla
    """
    try:
        img_data = base64.b64decode(base64_img.split(",")[1])
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        if intento < 2:
            return decode_image(base64_img, intento + 1)  # llamada recursiva
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

    # 📋 LISTA original desde BD
    usuarios_lista = obtener_usuarios()

    if not usuarios_lista:
        return jsonify({"mensaje": "No hay usuarios registrados"})

    # 🟡 COLA (FIFO)
    usuarios = deque(usuarios_lista)

    # 🥞 PILA (LIFO)
    pila_comparaciones = []

    # 📋 LISTA adicional
    distancias = []

    # 🌳 ÁRBOL (diccionario jerárquico)
    arbol_usuarios = {}

    # 🔗 GRAFO (relaciones)
    grafo = {}

    mejor_usuario = None
    mejor_distancia = 1
    mejor_id = None

    # =========================
    # 🔄 PROCESAMIENTO (COLA)
    # =========================
    while usuarios:
        u = usuarios.popleft()  # FIFO

        nombre = u["nombre"]
        ruta = u["imagen"]
        user_id = u["id"]

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

            print(f"{nombre} → {distancia}")

            # 📋 LISTA
            distancias.append(distancia)

            # 🥞 PILA
            pila_comparaciones.append((nombre, distancia))

            # 🌳 ÁRBOL
            if nombre not in arbol_usuarios:
                arbol_usuarios[nombre] = []
            arbol_usuarios[nombre].append(distancia)

            # 🔗 GRAFO
            grafo[nombre] = {
                "imagen": ruta,
                "distancia": distancia
            }

            # 🔎 BÚSQUEDA DEL MÍNIMO
            if distancia < mejor_distancia:
                mejor_distancia = distancia
                mejor_usuario = nombre
                mejor_id = user_id

        except Exception as e:
            print("Error:", e)

    # =========================
    # RESULTADO FINAL
    # =========================

    if mejor_usuario and mejor_distancia < 0.6:
        insertar_log(mejor_id, "exitoso")

        return jsonify({
            "mensaje": f"Acceso permitido: {mejor_usuario} 🔓",
            "confianza": float(mejor_distancia)
        })

    insertar_log(None, "fallido")

    return jsonify({"mensaje": "Acceso denegado ❌"})


# =========================
# 📋 LISTAR
# =========================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = obtener_usuarios()

    # 📋 LISTA POR COMPRENSIÓN
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