import requests
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from worq.models.models import Files

@view_config(route_name='file_preview', renderer='templates/file_preview.jinja2')
def file_preview_view(request):
    file_id = request.matchdict.get('id')
    file = request.dbsession.query(Files).filter_by(id=file_id).first()

    if not file:
        return HTTPNotFound()

    # Leer contenido si es txt
    content = None
    if file.filename.endswith('.txt'):
        try:
            response = requests.get(file.filepath)
            if response.status_code == 200:
                content = response.text
            else:
                content = '[Failed to load file]'
        except Exception as e:
            content = f'[Error: {e}]'

    return {
        'file': file,
        'txt_content': content,
    }
