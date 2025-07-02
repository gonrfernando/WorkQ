from pyramid.view import view_config
from worq.models.models import Files, TaskFiles
import logging

log = logging.getLogger(__name__)

@view_config(route_name='delete_file', request_method='POST', renderer='json')
def delete_file_view(request):
    file_id = request.POST.get('file_id')
    task_id = request.POST.get('task_id')  # If you need it for extra logic
    print("Received file_id:", file_id)
    print("Received task_id:", task_id)

    if not file_id:
        return {'status': 'error', 'message': 'Missing file_id'}

    try:
        archivo = (
            request.dbsession.query(Files)
            .filter_by(id=file_id)
            .first()
        )

        if not archivo:
            return {'status': 'error', 'message': 'File not found'}


        request.dbsession.query(TaskFiles).filter_by(file_id=file_id).delete()
        request.dbsession.delete(archivo)
        request.dbsession.flush()

        return {'status': 'ok', 'message': 'File deleted successfully'}

    except Exception as e:
        log.exception("Unexpected error during file deletion")
        return {'status': 'error', 'message': f"Unexpected error: {str(e)}"}
