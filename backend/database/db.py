import mysql.connector # type: ignore
from datetime import datetime


# =========================
# 🔌 CONEXIÓN A LA BASE DE DATOS
# =========================
def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="micho1234",
            database="smartaccess",
            auth_plugin="mysql_native_password"  # 🔥 clave
        )
    except Exception as e:
        print("Error conectando a la DB:", e)
        return None


# =========================
# ➕ INSERTAR USUARIO
# =========================
def insertar_usuario(nombre, imagen):
    """
    Inserta un nuevo usuario en la base de datos
    """
    db = conectar()

    if db is None:
        return False

    try:
        cursor = db.cursor()

        fecha = datetime.now()

        sql = """
        INSERT INTO usuarios (nombre, imagen, fecha_ingreso)
        VALUES (%s, %s, %s)
        """

        # 🔒 evita SQL injection
        cursor.execute(sql, (nombre, imagen, fecha))

        db.commit()

        return True

    except Exception as e:
        print("Error insertando usuario:", e)
        db.rollback()  # 🔥 importante si algo falla
        return False

    finally:
        cursor.close()
        db.close()


# =========================
# 📋 OBTENER USUARIOS
# =========================
def obtener_usuarios():
    """
    Obtiene todos los usuarios registrados
    """
    db = conectar()

    if db is None:
        return []

    try:
        cursor = db.cursor(dictionary=True)  # 🔥 devuelve diccionarios

        cursor.execute("SELECT * FROM usuarios")

        datos = cursor.fetchall()

        return datos

    except Exception as e:
        print("Error obteniendo usuarios:", e)
        return []

    finally:
        cursor.close()
        db.close()


# =========================
# 🔍 OBTENER USUARIO POR NOMBRE (EXTRA PRO)
# =========================
def obtener_usuario_por_nombre(nombre):
    """
    Busca un usuario específico por nombre
    """
    db = conectar()

    if db is None:
        return None

    try:
        cursor = db.cursor(dictionary=True)

        sql = "SELECT * FROM usuarios WHERE nombre = %s"
        cursor.execute(sql, (nombre,))

        usuario = cursor.fetchone()

        return usuario

    except Exception as e:
        print("Error buscando usuario:", e)
        return None

    finally:
        cursor.close()
        db.close()