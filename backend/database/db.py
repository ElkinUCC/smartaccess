import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="micho1234",  
        database="smartaccess"
    )

from datetime import datetime

def insertar_usuario(nombre, imagen):
    db = conectar()
    cursor = db.cursor()

    fecha = datetime.now()

    sql = "INSERT INTO usuarios (nombre, imagen, fecha_ingreso) VALUES (%s, %s, %s)"
    cursor.execute(sql, (nombre, imagen, fecha))

    db.commit()
    cursor.close()
    db.close()


def obtener_usuarios():
    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()

    cursor.close()
    db.close()

    return datos