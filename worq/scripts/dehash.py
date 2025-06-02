import bcrypt

# Hash generado previamente (copiado de tu sistema, base de datos, etc.)
stored_hash = b"$2b$12$AbdsxU8rQK/Qu1V82fhk6u3xRqnwODf7e/n.oUiO1/L0AS40q6T22"  # reemplaza esto con tu hash real

# Contraseña que quieres probar
password = "1234"  # reemplaza esto con la contraseña que estás probando

# Codificar y verificar
if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
    print("✅ La contraseña coincide con el hash.")
else:
    print("❌ La contraseña NO coincide con el hash.")
