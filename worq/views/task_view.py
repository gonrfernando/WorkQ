from pyramid.view import view_config
from worq.models.models import Projects


@view_config(route_name='task_view', renderer='worq:templates/task_view.jinja2')
def my_view(request):
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    #json_projects = [{"id": project.id, "name": project.name, 'icon_id':project.icon_name} for project in projects]
    active_project_id = request.params.get("project_id")
    active_project_id = 1
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)
    tasks = [
        {
            "title": "Task 1",
            "due_date": "2025-05-01",
            "priority": "High",
            "description": "Complete the project documentation.",
            "requirements": ["Write intro", "Add diagrams", "Review content"]
        },
        {
            "title": "Task 2",
            "due_date": "2025-05-05",
            "priority": "Medium",
            "description": "Prepare for the client meeting.",
            "requirements": ["Create slides", "Practice presentation"]
        },
    ]
    return {
        "projects": json_projects,
        "active_project": active_project,
        "tasks": tasks
    }
