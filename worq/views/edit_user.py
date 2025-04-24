from pyramid.view import view_config
from worq.models.models import Users, Areas, Roles, Countries, Projects
from sqlalchemy.exc import IntegrityError
import transaction  # Importar el manejador de transacciones


@view_config(route_name='edit_user', renderer='templates/edit_user.jinja2', request_method='GET')
def show_edit_user_form(request):
    users = request.dbsession.query(Users).all()
    countries = request.dbsession.query(Countries).all()
    areas = request.dbsession.query(Areas).all()
    roles = request.dbsession.query(Roles).all()
    projects = request.dbsession.query(Projects).all()

    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    users_data = [{"id": user.id, "email": user.email, "name": user.name} for user in users]

    return {
        'countries': countries,
        'areas': areas,
        'roles': roles,
        'projects': json_projects,
        'users': users_data  # Cambié el nombre para mayor claridad
    }

@view_config(route_name='edit_user', renderer='templates/edit_user.jinja2', request_method='PUT')
def edit_user_view(request):
    user_id = request.params.get('id')  # Obtener el ID del usuario
    name = request.params.get('name')
    email = request.params.get('email')
    tel = request.params.get('tel')
    passw = request.params.get('passw')
    country_id = int(request.params.get('country')) if request.params.get('country') else None
    area_id = int(request.params.get('area')) if request.params.get('area') else None
    role_id = int(request.params.get('role')) if request.params.get('role') else None

    # Buscar el usuario existente
    user = request.dbsession.query(Users).filter_by(id=user_id).first()

    if not user:
        return {
            'message': f"User with ID {user_id} not found.",
            'countries': request.dbsession.query(Countries).all(),
            'areas': request.dbsession.query(Areas).all(),
            'roles': request.dbsession.query(Roles).all(),
            'projects': [{"id": project.id, "name": project.name} for project in request.dbsession.query(Projects).all()]
        }

    # Actualizar los datos del usuario
    user.name = name
    user.email = email
    user.tel = tel
    user.passw = passw
    user.country_id = country_id
    user.area_id = area_id
    user.role_id = role_id

    try:
        # Confirmar la transacción
        with transaction.manager:
            request.dbsession.flush()
        message = "User successfully updated!"
    except IntegrityError:
        request.dbsession.rollback()
        message = "An error occurred while updating the user."

    return {
        'users': [{"id": user.id, "email": user.email} for user in request.dbsession.query(Users).all()],
        'countries': request.dbsession.query(Countries).all(),
        'areas': request.dbsession.query(Areas).all(),
        'roles': request.dbsession.query(Roles).all(),
        'projects': [{"id": project.id, "name": project.name} for project in request.dbsession.query(Projects).all()],
        'message': message
    }