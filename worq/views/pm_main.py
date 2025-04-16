from pyramid.view import view_config
@view_config(route_name='pm_main', renderer='worq:templates/pm_main.jinja2')
def my_view(request):
    #projects = DBSession.query(Project).all()
    #active_project_id = request.params.get("project_id")
    projects = {
        1: {"name": "Project A", "id": "1"},
        2: {"name": "Project B", "id": "2"},
        3: {"name": "Project C", "id": "3"},
    }
    # Simulating a database query
    active_project_id = 1
    return {
        "projects": projects,
        "active_project_id": active_project_id
    }