import os
import uuid
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from worq.scripts.s3_utils import upload_file_to_s3
from worq.models.models import Files, TaskFiles

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'docx', 'xlsx', 'txt'}

def secure_filename(filename):
    filename = os.path.basename(filename)
    filename = filename.replace(" ", "_")
    return ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@view_config(route_name='upload_file', request_method='POST')
def upload_view(request):
    try:
        archivo = request.POST['file']
        task_id = request.POST['task_id']
        input_file = archivo.file
        original_filename = archivo.filename
        content_type = archivo.type

        if not allowed_file(original_filename):
            request.session.flash('File extension not allowed', 'error')
            return HTTPFound(location=request.route_url('task_view'))

        sanitized_filename = secure_filename(original_filename)
        unique_filename = f"{uuid.uuid4().hex}_{sanitized_filename}"

        url = upload_file_to_s3(input_file, unique_filename, content_type)

        nuevo_archivo = Files(filename=sanitized_filename, filepath=url)
        request.dbsession.add(nuevo_archivo)
        request.dbsession.flush()

        relacion = TaskFiles(task_id=task_id, file_id=nuevo_archivo.id)
        request.dbsession.add(relacion)
        request.dbsession.flush()

        request.session.flash('File uploaded successfully', 'success')
        return HTTPFound(location=request.route_url('task_view'))
    except Exception as e:
        request.session.flash(f'Error: {str(e)}', 'error')
        return HTTPFound(location=request.route_url('task_view'))
