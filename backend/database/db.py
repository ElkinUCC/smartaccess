import sqlite3

def conectar():
    conn = sqlite3.connect("smartaccess.db")
    return conn

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def insertar_usuario(nombre):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO usuarios (nombre) VALUES (?)", (nombre,))
    
    conn.commit()
    conn.close()


def obtener_usuarios():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    conn.close()
    return usuarios