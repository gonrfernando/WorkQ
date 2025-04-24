from pyramid.view import view_config
from worq.models.models import Projects

@view_config(route_name='pm_main', renderer='templates/pm_main.jinja2', request_method='GET')
def pm_main_view(request):
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    return {
        "projects": json_projects,
        "active_project_id": active_project_id
    }

@view_config(route_name='pm_main', renderer='templates/pm_main.jinja2', request_method='POST')
def pm_view(request):
    
    
    
     
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    active_project_id = 1
    return {
        "projects": json_projects,
        "active_project_id": active_project_id
    }