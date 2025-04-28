from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements


@view_config(route_name='task_view', renderer='worq:templates/task_view.jinja2')
def my_view(request):
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    #json_projects = [{"id": project.id, "name": project.name, 'icon_id':project.icon_name} for project in projects]
    active_project_id = request.params.get("project_id")
    active_project_id = 1
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)
    
    dbtasks = request.dbsession.query(Tasks).filter_by(project_id = active_project_id).all()
    json_tasks = [{
        "id": task.id, 
        "title":task.title, 
        "description":task.description,
        "due_date":task.finished_date,
        "requirements":[{
            "id":requirement.id,
            "requirement":requirement.requirement,
            "is_completed":requirement.is_completed
        } for requirement in request.dbsession.query(TaskRequirements).filter_by(task_id = task.id).all()]
        } for task in dbtasks]
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
        {
            "title": "Task 3",
            "due_date": "2025-05-05",
            "priority": "Low",
            "description": "Prepare for the client meeting.",
            "requirements": ["Create slides", "Practice presentation"]
        },
        {
            "title": "Task 4",
            "due_date": "2025-05-05",
            "priority": "Medium",
            "description": "Prepare for the client meeting.",
            "requirements": ["Create slides", "Practice presentation"]
        },
        {
            "title": "Task 5",
            "due_date": "2025-05-05",
            "priority": "Medium",
            "description": "Prepare for the client meeting.",
            "requirements": ["Create slides", "Practice presentation"]
        },
    ]
    return {
        "projects": json_projects,
        "active_project": active_project,
        "tasks": json_tasks
    }
