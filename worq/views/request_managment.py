from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, Requests, TaskPriorities
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm import joinedload
from sqlalchemy import exists, and_
from pyramid.response import Response
from datetime import datetime


@view_config(route_name='request_management', renderer='worq:templates/request_management.jinja2')
def my_view(request):
    session = request.session
    projects = request.dbsession.query(Projects).all()
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')

    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    
    # Filtramos Tasks que tengan alguna Request con id=1
    dbtasks = (
        request.dbsession.query(Tasks)
        .options(joinedload(Tasks.requests), joinedload(Tasks.project)) 
        .filter(
            exists().where(
                and_(
                    Requests.task_id == Tasks.id,
                    Requests.status_id == 1
                )
            )
        )
        .all()
    )
    priority_map = {
        p.id: p.priority
        for p in request.dbsession.query(TaskPriorities).all()
    }
    
    json_tasks = [{
        "id": task.id, 
        "project_id": task.project_id,
        "project_name": task.project.name,  
        "title": task.title, 
        "description": task.description,
        "priority": priority_map.get(task.priority_id, "None"),
        "due_date": task.finished_date.strftime('%Y-%m-%d %H:%M:%S') if task.finished_date else "N/A",
        "requirements": [{
            "id": req.id,
            "requirement": req.requirement,
            "is_completed": req.is_completed
        } for req in task.task_requirements],
        "requests": [
            {
                "id": req.id,
                "user_id": req.user_id,
                "status": req.status.status_name if req.status else "N/A",
                "reason": req.reason,
                "date": req.request_date.strftime('%Y-%m-%d %H:%M:%S') if req.request_date else "N/A",
                "action_type": req.action_type,
                "accepted_by": req.accepted_by,
                "rejected_by": req.rejected_by
            }
            for req in sorted(task.requests, key=lambda r: (
                (1 if r.accepted_by or r.rejected_by else 0),
                r.request_date or datetime.max
            ))
        ]
    } for task in dbtasks]

    has_requests = any(task["requests"] for task in json_tasks)
    
    return {
        "projects": json_projects,
        "tasks": json_tasks,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role,
        'has_requests': has_requests
    }


@view_config(route_name='handle_request_action', request_method='POST', renderer='json')
def handle_request_action(request):
    try:
        data = request.json_body
        request_id = data.get('request_id')
        action = data.get('action')
        user_id = request.session.get('user_id')

        if not user_id:
            return Response(json_body={'error': 'Unauthorized'}, status=401)

        req_obj = request.dbsession.query(Requests).get(request_id)
        if not req_obj:
            return Response(json_body={'error': 'Request not found'}, status=404)

        if action == "accept":
            req_obj.accepted_by = user_id
            req_obj.status_id = 2  # status aceptada
        elif action == "reject":
            req_obj.rejected_by = user_id
            req_obj.status_id = 3  # status rechazada
        else:
            return Response(json_body={'error': 'Invalid action'}, status=400)

        request.dbsession.flush()
        return {"message": "Request updated"}

    except Exception as e:
        print(f"Error: {e}")
        return Response(json_body={'error': str(e)}, status=500)
