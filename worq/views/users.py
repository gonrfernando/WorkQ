from pyramid.view import view_config
from pyramid.response import Response
from countryinfo import CountryInfo
from pyramid.httpexceptions import HTTPFound
from worq.models.models import UsersProjects, Users, Countries, Areas, Roles
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
    project_ids = request.dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
    json_projects = [{"id": project.project_id, "name": project.project.name} for project in project_ids]
    
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

        request.dbsession.flush()

        return {"success": True, "message": "User updated successfully"}
    except Exception as e:
        return {"error": str(e)}
