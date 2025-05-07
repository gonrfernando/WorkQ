from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from worq.models.models import *

@view_config(route_name='add_user', renderer='templates/add_user.jinja2', request_method='GET')
def add_user_form_view(request):
    # Datos para renderizar el formulario
    departments = [
        {'id': 1, 'name': 'Engineering'},
        {'id': 2, 'name': 'HR'},
        {'id': 3, 'name': 'Marketing'}
    ]
    roles = [
        {'id': 1, 'name': 'Admin'},
        {'id': 2, 'name': 'User'},
        {'id': 3, 'name': 'Guest'}
    ]
    return {
        'departments': departments,
        'roles': roles
    }

@view_config(route_name='add_user', request_method='POST')
def add_user_submit_view(request):
    # Procesar los datos enviados desde el formulario
    name = request.POST.get('name')
    email_address = request.POST.get('email_address')
    number = request.POST.get('number')
    department = request.POST.get('department')
    role = request.POST.get('role')

    # Aquí puedes agregar lógica para guardar los datos en la base de datos
    print(f"Received data: Name={name}, Email={email_address}, Number={number}, Department={department}, Role={role}")

    # Redirigir a otra página después de procesar los datos
    return HTTPFound(location='/success')  # Cambia '/success' por la ruta deseada