from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import SQLAlchemyError
from worq.models.models import Files, TaskFiles
from worq.scripts.s3_utils import generate_presigned_url
import logging

log = logging.getLogger(__name__)

@view_config(route_name='files_by_task', renderer='json', request_method='GET')
def files_by_task_view(request):
    task_id = request.params.get('task_id')

    # Validación del parámetro
    if not task_id:
        return {'status': 'error', 'message': 'Missing task_id'}

    try:
        archivos = (
            request.dbsession.query(Files)
            .join(TaskFiles, Files.id == TaskFiles.file_id)
            .filter(TaskFiles.task_id == task_id)
            .all()
        )
    except SQLAlchemyError as e:
        log.error(f"Database error retrieving files for task {task_id}: {e}")
        return {'status': 'error', 'message': 'Database error while retrieving files'}

    result = []
    for archivo in archivos:
        try:
            url = generate_presigned_url(archivo.filepath)
        except Exception as e:
            log.warning(f"Could not generate presigned URL for file {archivo.id}: {e}")
            url = None  # Deja la URL como None si no se puede generar

        result.append({
            'id': archivo.id,
            'filename': archivo.filename,
            'url': url
        })

    return {'status': 'ok', 'files': result}
