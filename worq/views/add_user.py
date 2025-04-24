from pyramid.view import view_config
from worq.models.models import Users, Areas, Roles, Countries, Projects
from sqlalchemy.exc import IntegrityError
import transaction  # Importar el manejador de transacciones


@view_config(route_name='add_user', renderer='templates/add_user.jinja2', request_method='GET')
def show_add_user_form(request):
    countries = request.dbsession.query(Countries).all()
    areas = request.dbsession.query(Areas).all()
    roles = request.dbsession.query(Roles).all()
    projects = request.dbsession.query(Projects).all()

    json_projects = [{"id": project.id, "name": project.name} for project in projects]

    return {
        'countries': countries,
        'areas': areas,
        'roles': roles,
        'projects': json_projects,
        'message': ''
    }

@view_config(route_name='add_user', renderer='templates/add_user.jinja2', request_method='POST')
def add_user_test_view(request):

    name = request.params.get('name')
    email = request.params.get('email')
    tel = request.params.get('tel')
    passw = request.params.get('passw')
    country_id = int(request.params.get('country')) if request.params.get('country') else None
    area_id = int(request.params.get('area')) if request.params.get('area') else None
    role_id = int(request.params.get('role')) if request.params.get('role') else None

    new_user = Users(
            name=name,
            email=email,
            tel=tel,
            passw=passw,
            country_id=country_id,
            area_id=area_id,
            role_id=role_id
        )
    print(f"Name: {name}, Email: {email}, Tel: {tel}, Passw: {passw}, Country: {country_id}, Area: {area_id}, Role: {role_id}")
    try:
            request.dbsession.add(new_user)
            # Usar transaction.manager para confirmar la transacción
            with transaction.manager:
                request.dbsession.flush()  # Asegurar que los datos se escriban en la base de datos
            message = "User successfully added!"
    except IntegrityError:
            request.dbsession.rollback()  # Deshacer la transacción en caso de error
            message = "An error occurred while adding the user."
    countries = request.dbsession.query(Countries).all()
    areas = request.dbsession.query(Areas).all()
    roles = request.dbsession.query(Roles).all()
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]

    return {
        'countries': countries,
        'areas': areas,
        'roles': roles,
        'projects': json_projects,
        'message': message
    }
