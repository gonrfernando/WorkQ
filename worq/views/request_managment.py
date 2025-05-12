from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError

@view_config(route_name='request_management', renderer='worq:templates/request_management.jinja2')
def my_view(request):
    session = request.session
    projects = request.dbsession.query(Projects).all()
    if not 'user_name' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')

    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    
    dbtasks = request.dbsession.query(Tasks).all()
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
        "tasks": json_tasks,
        #'user_name': user_name,
        #'user_email': user_email,
        #'user_role': user_role
    }

