from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from worq.views.metrics import REQUEST_COUNT

@view_config(route_name='logout')
def logout_view(request):
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
    request.session.invalidate()  # Elimina todos los datos de la sesión
    return HTTPFound(location=request.route_url('sign_in'))