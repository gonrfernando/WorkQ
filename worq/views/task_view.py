from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements


@view_config(route_name='task_view', renderer='worq:templates/task_view.jinja2')
def my_view(request):
    
    projects = request.dbsession.query(Projects).all()
    
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    active_project_id = 1
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)
    
    dbtasks = request.dbsession.query(Tasks).filter_by(project_id = active_project_id).all()
    
    priorities = {
        1: "Low",
        2: "Avg",
        3: "High"
    }
    
    json_tasks = [{
        "id": task.id, 
        "title":task.title, 
        "description":task.description,
        "priority": priorities.get(task.priority, "None"), 
        "due_date":task.finished_date,
        "requirements":[{
            "id":requirement.id,
            "requirement":requirement.requirement,
            "is_completed":requirement.is_completed
        } for requirement in request.dbsession.query(TaskRequirements).filter_by(task_id = task.id).all()]
        } for task in dbtasks]
    
    return {
        "projects": json_projects,
        "active_project": active_project,
        "tasks": json_tasks
    }

