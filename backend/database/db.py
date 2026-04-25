import mysql.connector # type: ignore
from datetime import datetime


# =========================
# 🔌 CONEXIÓN
# =========================
def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="micho1234",
            database="smartaccess",
            auth_plugin="mysql_native_password"
        )
    except Exception as e:
        print("Error DB:", e)
        return None


# =========================
# ➕ INSERTAR USUARIO
# =========================
def insertar_usuario(nombre, imagen):
    db = conectar()
    if db is None:
        return False

    try:
        cursor = db.cursor()
        sql = """
        INSERT INTO usuarios (nombre, imagen, fecha_ingreso)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (nombre, imagen, datetime.now()))
        db.commit()
        return True

    except Exception as e:
        print("Error insertando usuario:", e)
        db.rollback()
        return False

    finally:
        cursor.close()
        db.close()


# =========================
# 📋 OBTENER USUARIOS
# =========================
def obtener_usuarios():
    db = conectar()
    if db is None:
        return []

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        return cursor.fetchall()

    except Exception as e:
        print("Error obteniendo usuarios:", e)
        return []

    finally:
        cursor.close()
        db.close()


# =========================
# 📝 INSERTAR LOG
# =========================
def insertar_log(usuario_id, resultado):
    db = conectar()
    if db is None:
        return False

    try:
        cursor = db.cursor()
        sql = """
        INSERT INTO log_accesos (usuario_id, resultado)
        VALUES (%s, %s)
        """
        cursor.execute(sql, (usuario_id, resultado))
        db.commit()
        return True

    except Exception as e:
        print("Error insertando log:", e)
        db.rollback()
        return False

    finally:
        cursor.close()
        db.close()