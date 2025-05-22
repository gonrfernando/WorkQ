from pyramid.view import view_config
from worq.scripts.s3_utils import upload_file_to_s3
from worq.models.models import Files  

@view_config(route_name='upload_file', renderer='json', request_method='POST')
def upload_view(request):
    input_file = request.POST['file'].file
    filename = request.POST['file'].filename
    content_type = request.POST['file'].type

    # Subir a S3
    url = upload_file_to_s3(input_file, filename, content_type)

    # Guardar en base de datos
    nuevo_archivo = Files(filename=filename, filepath=url)
    request.dbsession.add(nuevo_archivo)
    request.dbsession.flush()

    return {'status': 'ok', 'url': url}
