import os
import uuid
import mimetypes
from pyramid.view import view_config
from worq.scripts.s3_utils import upload_file_to_s3
from worq.models.models import Files
from worq.views.metrics import REQUEST_COUNT

# Extensiones permitidas (puedes ajustarlas)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'docx', 'xlsx', 'txt'}

def secure_filename(filename):
    """
    Sanitiza el nombre del archivo para evitar inyecciones o caracteres maliciosos.
    """
    filename = os.path.basename(filename)  # Evita path traversal
    filename = filename.replace(" ", "_")  # Opcional: reemplaza espacios
    # Solo caracteres alfanuméricos, guiones y puntos
    return ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))

def allowed_file(filename):
    """
    Verifica que el archivo tenga una extensión permitida.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@view_config(route_name='upload_file', renderer='json', request_method='POST')
def upload_view(request):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
    archivo = request.POST['file']
    input_file = archivo.file
    original_filename = archivo.filename
    content_type = archivo.type

    # Validación y sanitización
    if not allowed_file(original_filename):
        return {'status': 'error', 'message': 'Extensión de archivo no permitida'}

    sanitized_filename = secure_filename(original_filename)
    unique_filename = f"{uuid.uuid4().hex}_{sanitized_filename}"

    # Subir a S3
    url = upload_file_to_s3(input_file, unique_filename, content_type)

    # Guardar en base de datos
    nuevo_archivo = Files(filename=sanitized_filename, filepath=url)
    request.dbsession.add(nuevo_archivo)
    request.dbsession.flush()

    return {'status': 'ok', 'url': url}
