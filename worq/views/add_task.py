from pyramid.view import view_config
from pyramid.response import Response
from worq.models.models import UsersProjects, Roles, Users
from sqlalchemy.exc import SQLAlchemyError
from pyramid.httpexceptions import HTTPFound

@view_config(route_name='add_task', renderer='worq:templates/add_task.jinja2')
def task_creation_view(request):
    session = request.session
    if not 'user_name' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    active_project_id = session.get("project_id")
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    user_id = session.get('user_id')
    
    project_ids = request.dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
    json_projects = [{"id": project.project_id, "name": project.project.name} for project in project_ids]
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)
    users = request.dbsession.query(Users).all()
    roles = request.dbsession.query(Roles).all()

    json_users = [{"id": user.id, 
                   "name": user.name, 
                   "email": user.email,
                   "tel": user.tel, 
                   "passw": user.passw, 
                   "country_id": user.country_id,
                   "area_id": user.area_id,
                   "role_id": user.role_id} for user in users]
    return {
        "users": json_users,
        "roles": [{"id": role.id, "name": role.name} for role in roles],
        "projects": json_projects,
        "active_project_id": active_project_id,
        "active_project": active_project,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role
    }