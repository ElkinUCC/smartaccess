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