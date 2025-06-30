from pyramid.view import view_config
from worq.models.models import Files, TaskFiles
from sqlalchemy.orm import load_only
from worq.scripts.s3_utils import delete_file_from_s3
import logging

log = logging.getLogger(__name__)

@view_config(route_name='delete_file', request_method='POST', renderer='json')
def delete_file_view(request):
    file_id = request.POST.get('file_id')

    if not file_id:
        return {'status': 'error', 'message': 'Missing file_id'}

    try:
        archivo = (
            request.dbsession.query(Files)
            .options(load_only(Files.id, Files.filename, Files.filepath))
            .filter_by(id=file_id)
            .first()
        )

        if not archivo:
            return {'status': 'error', 'message': 'File not found'}

        s3_key = archivo.filepath

        try:
            success = delete_file_from_s3(s3_key)
        except Exception as e:
            log.exception("Error deleting from S3")
            return {'status': 'error', 'message': f"Exception deleting from S3: {str(e)}"}

        if not success:
            return {'status': 'error', 'message': 'Could not delete from S3'}

        request.dbsession.query(TaskFiles).filter_by(file_id=file_id).delete()
        request.dbsession.delete(archivo)
        request.dbsession.flush()

        return {'status': 'ok', 'message': 'File deleted successfully'}

    except Exception as e:
        log.exception("Unexpected error during file deletion")
        return {'status': 'error', 'message': f"Unexpected error: {str(e)}"}
