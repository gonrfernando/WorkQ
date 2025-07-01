from pyramid.view import view_config
from pyramid.response import Response
from countryinfo import CountryInfo
from pyramid.httpexceptions import HTTPFound
from worq.models.models import UsersProjects, Users, Countries, Areas, Roles, Projects, Notifications, UsersNotifications
import datetime
from sqlalchemy.exc import SQLAlchemyError

@view_config(route_name='edit_user', renderer='templates/edit_user.jinja2')
def my_view(request):
    session = request.session
    if not 'user_name' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    active_project_id = session.get("project_id")
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    user_id = session.get('user_id')
    
    
    users = request.dbsession.query(Users).all()
    countries = request.dbsession.query(Countries).all()
    areas = request.dbsession.query(Areas).all()
    roles = request.dbsession.query(Roles).all()
    if user_role in ['superadmin', 'admin']:
        user_projects = (
            request.dbsession.query(Projects)
            .filter(Projects.state_id != 2)  # Filtrar los que no tienen state_id=2
            .all()
        )
    else:
        user_projects = (
            request.dbsession.query(Projects)
            .join(UsersProjects)
            .filter(
                UsersProjects.user_id == user_id,
                Projects.state_id != 2  # Filtrar también aquí
            )
            .all()
        )
 
    json_projects = [{"id": project.id, "name": project.name} for project in user_projects]
    
    json_users = [{"id": user.id, 
                   "name": user.name, 
                   "email": user.email,
                   "tel": user.tel, 
                   "country_id": user.country_id,
                   "area_id": user.area_id,
                   "role_id": user.role_id} for user in users]

    json_countries = []
    for country in countries:
        country_info = CountryInfo(country.name)
        try:
            calling_codes = country_info.info().get("callingCodes", [])
            prefix = calling_codes[0] if calling_codes else ""
        except KeyError:
            prefix = ""
        json_countries.append({"id": country.id, "name": country.name, "prefix": prefix})

    return {
        "projects": json_projects,
        "active_project_id": active_project_id,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role,
        "users": json_users,
        "countries": json_countries,
        "areas": [{"id": area.id, "area": area.area} for area in areas],
        "roles": [{"id": role.id, "name": role.name} for role in roles]
    }

@view_config(route_name='update_user', request_method='POST', renderer='json')
def update_user(request):
    try:
        user_id = request.json_body.get("user_id")
        if not user_id:
            return {"error": "User ID is required"}

        user = request.dbsession.query(Users).filter(Users.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        user.name = request.json_body.get("name", user.name)
        user.email = request.json_body.get("email", user.email)
        user.tel = request.json_body.get("tel", user.tel)
        user.country_id = int(request.json_body.get("country_id", user.country_id))
        user.area_id = int(request.json_body.get("area_id", user.area_id))
        user.role_id = int(request.json_body.get("role_id", user.role_id))

        new_passw = request.json_body.get("passw")
        if new_passw:
            user.passw = new_passw

        # --- Notificación de edición de usuario ---

        notif = Notifications(
            type_id=12,  # ID para "Usuario editado"
            date=datetime.datetime.utcnow(),
            state_id=4   # Ajusta según tu tabla de estados (por ejemplo, 4 = "Pendiente" o "No leído")
        )
        request.dbsession.add(notif)
        request.dbsession.flush()  # Para obtener notif.id

        request.dbsession.add(UsersNotifications(
            noti_id=notif.id,
            user_id=user.id  # Notifica al usuario editado
        ))
        # --- Fin notificación ---

        request.dbsession.flush()

        return {"success": True, "message": "User updated successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}