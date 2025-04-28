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

@view_config(route_name='create_project', request_method='POST', renderer='json')
def create_project(request):
    try:
        name = request.POST.get('p_name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')

        if not name or not start_date or not description:
            return {"success": False, "error": "Missing fields"}

        new_project = Projects(
            name=name,
            startdate=start_date,
            enddate=end_date,  # Pones enddate igual a startdate si no se usa
            creationdate=datetime.date.today(),
            state_id=1  # o el estado por defecto
        )

        request.dbsession.add(new_project)
        request.dbsession.flush()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
