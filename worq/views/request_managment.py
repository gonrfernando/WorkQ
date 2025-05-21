from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, Requests
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError
from sqlalchemy.orm import joinedload
from sqlalchemy import exists

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
    
    dbtasks = (
        request.dbsession.query(Tasks)
        .options(joinedload(Tasks.requests))
        .filter(exists().where(Requests.task_id == Tasks.id))
        .all()
    )
    priorities = {
        1: "Low",
        2: "Avg",
        3: "High"
    }
    
    json_tasks = [{
        "id": task.id, 
        "title": task.title, 
        "description": task.description,
        "priority": priorities.get(task.priority, "None"), 
        "due_date": task.finished_date.strftime('%Y-%m-%d %H:%M:%S') if task.finished_date else "N/A",
        "requirements": [{
            "id": req.id,
            "requirement": req.requirement,
            "is_completed": req.is_completed
        } for req in task.task_requirements],
        "requests": [{
            "id": req.id,
            "user_id": req.user_id,
            "status": req.status.status_name if req.status else "N/A",
            "reason": req.reason,
            "date": req.request_date.strftime('%Y-%m-%d %H:%M:%S') if req.request_date else "N/A",
            "action_type": req.action_type
        } for req in task.requests]
    } for task in dbtasks]


    return {
        "projects": json_projects,
        "tasks": json_tasks,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role
    }

