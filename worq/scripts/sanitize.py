import os
import re
from werkzeug.utils import secure_filename

# Configuración
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    """
    Verifica si el archivo tiene una extensión permitida.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename):
    """
    Sanitiza el nombre del archivo eliminando caracteres peligrosos.
    """
    filename = secure_filename(filename)  # Usa Werkzeug para sanitizar
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)  # Reemplaza caracteres no válidos

def validate_file_size(file):
    """
    Verifica si el tamaño del archivo es menor al máximo permitido.
    """
    file.seek(0, os.SEEK_END)  # Mueve el puntero al final del archivo
    file_size = file.tell()  # Obtiene el tamaño del archivo
    file.seek(0)  # Regresa el puntero al inicio
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE / (1024 * 1024)} MB")

def sanitize_file(file, filename):
    """
    Sanitiza y valida un archivo.
    - Verifica el tipo de archivo.
    - Verifica el tamaño del archivo.
    - Sanitiza el nombre del archivo.
    """
    if not allowed_file(filename):
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    validate_file_size(file)
    sanitized_name = sanitize_filename(filename)
    return sanitized_name