from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from worq.models.models import Files

@view_config(route_name='download_file', request_method='GET')
def download_file_view(request):
    file_id = request.params.get('id')
    archivo = request.dbsession.query(Files).filter_by(id=file_id).first()

    if not archivo:
        return {'status': 'error', 'message': 'Archivo no encontrado'}

    return HTTPFound(location=archivo.filepath)
