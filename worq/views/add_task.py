from pyramid.view import view_config
from pyramid.response import Response
from worq.models.models import Projects, Roles, Users
from sqlalchemy.exc import SQLAlchemyError

@view_config(route_name='add_task', renderer='worq:templates/add_task.jinja2')
def task_creation_view(request):
    projects = request.dbsession.query(Projects).all()
    users = request.dbsession.query(Users).all()
    roles = request.dbsession.query(Roles).all()

    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    json_users = [{"id": user.id, 
                   "name": user.name, 
                   "email": user.email,
                   "tel": user.tel, 
                   "passw": user.passw, 
                   "country_id": user.country_id,
                   "area_id": user.area_id,
                   "role_id": user.role_id} for user in users]
    return {
        "projects": json_projects,
        "users": json_users,
        "roles": [{"id": role.id, "name": role.name} for role in roles]
    }