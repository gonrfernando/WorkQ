import chardet

def clean_null_bytes_safe(file_path):
    try:
        # Detectar codificación
        with open(file_path, 'rb') as f:
            raw = f.read()
            result = chardet.detect(raw)
            encoding = result['encoding'] or 'utf-8'
            print(f"Codificación detectada: {encoding}")

        # Decodificar respetando codificación original
        text = raw.decode(encoding, errors='ignore')
        cleaned_text = text.replace('\x00', '')

        # Hacer backup
        with open(file_path + ".bak", 'wb') as backup:
            backup.write(raw)

        # Guardar archivo limpio
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(cleaned_text)

        print(f"Archivo limpio y guardado: {file_path}")
        print(f"Backup creado: {file_path}.bak")

    except Exception as e:
        print(f"Error al limpiar el archivo: {e}")

if __name__ == "__main__":
    FILE_PATH = r"C:\Users\axelo1\worq\worq\models\models.py"  # 👈 Modifica si es otro archivo
    clean_null_bytes_safe(FILE_PATH)
