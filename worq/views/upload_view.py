import os
from pyramid.view import view_config
from pyramid.response import Response
from worq.scripts.sanitize import sanitize_file

UPLOAD_FOLDER = 'uploads'  # Directorio donde se guardarán los archivos

@view_config(route_name='upload_file', request_method='POST', renderer='json')
def upload_file_view(request):
    try:
        # Verifica si el formulario contiene un archivo
        if 'file' not in request.POST:
            return {"success": False, "error": "No file part in the request"}

        # Obtén el archivo y su nombre
        file = request.POST['file'].file
        filename = request.POST['file'].filename

        # Sanitiza y valida el archivo
        sanitized_name = sanitize_file(file, filename)

        # Guarda el archivo en el directorio de subida
        upload_path = os.path.join(UPLOAD_FOLDER, sanitized_name)
        with open(upload_path, 'wb') as output_file:
            output_file.write(file.read())

        return {"success": True, "message": "File uploaded successfully", "filename": sanitized_name}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": "An unexpected error occurred"}