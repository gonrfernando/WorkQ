from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

@view_config(route_name='logout')
def logout_view(request):
    request.session.invalidate()  # Elimina todos los datos de la sesión
    return HTTPFound(location=request.route_url('sign_in'))