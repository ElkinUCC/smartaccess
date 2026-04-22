from flask import Flask, request, jsonify
from database.db import crear_tabla, insertar_usuario, obtener_usuarios
from collections import deque

app = Flask(__name__)

# =========================
# BASE DE DATOS INICIAL
# =========================
crear_tabla()

# =========================
# ESTRUCTURAS DE DATOS
# =========================

# Lista en memoria
usuarios_memoria = []

# Cola de ingresos (FIFO)
cola_ingresos = deque()

# =========================
# ÁRBOL BINARIO SIMPLE
# =========================

class Nodo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.izq = None
        self.der = None


raiz = None


def insertar_arbol(raiz, nombre):
    if raiz is None:
        return Nodo(nombre)

    if nombre < raiz.nombre:
        raiz.izq = insertar_arbol(raiz.izq, nombre)
    else:
        raiz.der = insertar_arbol(raiz.der, nombre)

    return raiz


def buscar_arbol(raiz, nombre):
    if raiz is None:
        return False

    if raiz.nombre == nombre:
        return True

    if nombre < raiz.nombre:
        return buscar_arbol(raiz.izq, nombre)

    return buscar_arbol(raiz.der, nombre)


# =========================
# RUTAS
# =========================

@app.route("/")
def home():
    return "SmartAccess funcionando 🔥"


# 📋 Obtener usuarios desde BD
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    usuarios = obtener_usuarios()

    lista = []
    for u in usuarios:
        lista.append({
            "id": u[0],
            "nombre": u[1]
        })

    return jsonify(lista)


# ➕ Crear usuario
@app.route("/usuarios", methods=["POST"])
def crear_usuario():
    global raiz

    data = request.json
    nombre = data.get("nombre")

    # BD
    insertar_usuario(nombre)

    # Lista en memoria
    usuarios_memoria.append(nombre)

    # Cola de ingreso
    cola_ingresos.append(nombre)

    # Árbol
    raiz = insertar_arbol(raiz, nombre)

    return jsonify({"mensaje": "Usuario creado"})


# 🧠 Ver memoria (lista)
@app.route("/memoria", methods=["GET"])
def ver_memoria():
    return jsonify(usuarios_memoria)


# ⏳ Ver cola
@app.route("/cola", methods=["GET"])
def ver_cola():
    return jsonify(list(cola_ingresos))


# 🔍 Buscar en árbol
@app.route("/buscar/<nombre>", methods=["GET"])
def buscar(nombre):
    encontrado = buscar_arbol(raiz, nombre)

    return jsonify({
        "nombre": nombre,
        "encontrado": encontrado
    })


# =========================
# EJECUCIÓN
# =========================

if __name__ == "__main__":
    app.run(debug=True)