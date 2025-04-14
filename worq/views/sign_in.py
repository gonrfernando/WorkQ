from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest
from worq.models.modelos import Users

@view_config(route_name='sign_in', renderer='templates/sign_in.jinja2')
def sign_in_view(request):
    try:
        if request.method == 'POST':
            # Obtener datos del formulario
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()

            # Validar que los campos no estén vacíos
            if not email:
                return {'message': 'Email is required'}
            if not password:
                return {'message': 'Password is required'}

            # Validar formato del correo electrónico
            if '@' not in email:
                return {'message': 'Invalid email address'}

            dbsession = request.dbsession
            
            # Consultar la base de datos
            user = dbsession.query(Users).filter(Users.email==email).first()
            
            # Comparar contraseñas
            if user and user.password == password:
                return HTTPFound(location=request.route_url('home'))
            else:
                return {'message': 'Invalid email or password'}

        return {}
    except Exception as e:
        # Registrar el error
        print(f"Error: {e}")
        raise HTTPInternalServerError("An unexpected error occurred.")