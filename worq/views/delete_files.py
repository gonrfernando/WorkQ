from pyramid.view import view_config
from worq.models.models import Files, TaskFiles
from sqlalchemy.orm import load_only
from worq.scripts.s3_utils import delete_file_from_s3

@view_config(route_name='delete_file', request_method='POST', renderer='json')
def delete_file_view(request):
    file_id = request.POST.get('file_id')

    archivo = request.dbsession.query(Files).options(load_only(Files.id, Files.filename, Files.filepath)).filter_by(id=file_id).first()

    if not archivo:
        return {'status': 'error', 'message': 'File not found'}

    # Extraer la key (filename único guardado en filepath)
    s3_key = archivo.filepath

    # Eliminar de S3
    success = delete_file_from_s3(s3_key)

    if not success:
        return {'status': 'error', 'message': 'Could not delete from S3'}

    # Eliminar de la base de datos
    request.dbsession.query(TaskFiles).filter_by(file_id=file_id).delete()
    request.dbsession.delete(archivo)
    request.dbsession.flush()

    return {'status': 'ok', 'message': 'File deleted successfully'}
