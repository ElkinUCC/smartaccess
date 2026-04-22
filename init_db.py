from database.db import crear_tabla, insertar_usuario, obtener_usuarios

crear_tabla()

# Insertar datos de prueba
insertar_usuario("Elkin")
insertar_usuario("Maria")

# Mostrar usuarios
usuarios = obtener_usuarios()

print("Usuarios en la base de datos:")
for u in usuarios:
    print(u)