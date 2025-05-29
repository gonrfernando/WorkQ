import bcrypt

# Contraseña que quieres hashear
password = "projectmanager" # Reemplaza esto por la contraseña real

# Generar el hash
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

# Mostrar el resultado
print("Hash generado:")
print(hashed.decode())
