from pyramid.view import view_config
from worq.models.models import Projects

@view_config(route_name='add_user', renderer='templates/test.jinja2')
def add_user_test_view(request):
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
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    active_project_id = 1
    return {
        "projects": json_projects,
        "active_project_id": active_project_id,
        'departments': departments,
        'roles': roles
    }