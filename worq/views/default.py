from pyramid.view import view_config
from worq.models.models import Projects

@view_config(route_name='home', renderer='worq:templates/workq_main.jinja2')
def my_view(request):
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    active_project_id = 1
    # Simulating a database query
    active_project_id = 1
    session = request.session
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    return {
        "projects": json_projects,
        "active_project_id": active_project_id,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role
    }
