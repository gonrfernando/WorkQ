from pyramid.view import view_config
from worq.models.models import Files, TaskFiles
from worq.scripts.s3_utils import generate_presigned_url
@view_config(route_name='files_by_task', renderer='json', request_method='GET')
def files_by_task_view(request):
    task_id = request.params.get('task_id')
    if not task_id:
        return {'status': 'error', 'message': 'Missing task_id'}

    archivos = (
        request.dbsession.query(Files)
        .join(TaskFiles, Files.id == TaskFiles.file_id)
        .filter(TaskFiles.task_id == task_id)
        .all()
    )

    result = [
        {
            'id': archivo.id,
            'filename': archivo.filename,
            'url': generate_presigned_url(archivo.filepath)
        }
        for archivo in archivos
    ]
    return {'status': 'ok', 'files': result}
