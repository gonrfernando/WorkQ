from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, Requests, TaskPriorities
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.orm import joinedload
from sqlalchemy import exists, and_
from pyramid.response import Response
from datetime import datetime
import logging
log = logging.getLogger(__name__)

@view_config(route_name='request_management', renderer='worq:templates/request_management.jinja2')
def my_view(request):
    session = request.session
    projects = request.dbsession.query(Projects).all()
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    if session.get('user_role') not in ('admin', 'superadmin'):
        print(f"[WARNING] Acceso denegado. Rol actual: {session.get('user_role')}")
        return HTTPFound(location=request.route_url('task_view'))
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')

    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    
    types = [
        {"id": 3, "name": "All Requests"},
        {"id": 2, "name": "Task"},
        {"id": 1, "name": "Project"},   
    ]
    # Obtener el type_id de los parámetros GET, con default en 3
    active_type_id = int(request.GET.get('type_id', 3))
    active_type = next((t for t in types if t["id"] == active_type_id), None)


    # MAPEO PRIORIDADES
    priority_map = {
        p.id: p.priority
        for p in request.dbsession.query(TaskPriorities).all()
    }

    # TASKS CON REQUESTS
    tasks_query = (
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
    )
    if active_type_id == 2:  # Solo Tasks
        dbtasks = tasks_query.all()
    else:
        dbtasks = tasks_query.all()

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

    # PROJECT REQUESTS (sin task_id)
    project_requests_query = (
        request.dbsession.query(Projects)
        .options(joinedload(Projects.requests))
        .filter(
            exists().where(
                and_(
                    Requests.project_id == Projects.id,
                    Requests.task_id.is_(None),
                    Requests.status_id == 1
                )
            )
        )
    )
    if active_type_id == 1:  # Solo Projects
        dbprojects = project_requests_query.all()
    else:
        dbprojects = project_requests_query.all()

    json_projects_with_requests = [{
        "id": proj.id,
        "name": proj.name,
        "start_date": proj.startdate.strftime('%Y-%m-%d') if proj.startdate else "N/A",
        "end_date": proj.enddate.strftime('%Y-%m-%d') if proj.enddate else "N/A",
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
            for req in sorted(
                [r for r in proj.requests if r.task_id is None],
                key=lambda r: (
                    (1 if r.accepted_by or r.rejected_by else 0),
                    r.request_date or datetime.max
                )
            )
        ]
    } for proj in dbprojects]


    has_task_requests = any(task["requests"] for task in json_tasks)
    has_project_requests = any(proj["requests"] for proj in json_projects_with_requests)
    has_requests = has_task_requests or has_project_requests

    return {
        "projects": json_projects,
        "tasks": json_tasks,
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "has_requests": has_requests,
        "has_task_requests": has_task_requests,
        "has_project_requests": has_project_requests,
        "types": types,
        "active_type": active_type,
        "projects_requests": json_projects_with_requests
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
            req_obj.status_id = 2  # aceptada
        elif action == "reject":
            req_obj.rejected_by = user_id
            req_obj.status_id = 3  # rechazada
        else:
            return Response(json_body={'error': 'Invalid action'}, status=400)

        request.dbsession.flush()

        response_data = {
            "message": "Request updated",
            "project_id": req_obj.project_id,
            "task_id": req_obj.task_id,
        }


        return response_data

    except Exception as e:
        print(f"Error: {e}")
        return Response(json_body={'error': str(e)}, status=500)


@view_config(route_name='prepare_edit_task', request_method='POST', renderer='json')
def prepare_edit_task_view(request):
    try:
        data = request.json_body
        task_id = data.get("task_id")
        if not task_id:
            return {"success": False, "error": "Task ID is required."}

        request.session['edit_task_id'] = task_id
        print(f"[INFO] task_id {task_id} guardado en sesión.")
        return {"success": True}
    except Exception as e:
        print(f"[ERROR] Error al preparar tarea para edición: {e}")
        return {"success": False, "error": str(e)}

@view_config(route_name='prepare_edit_project', request_method='POST', renderer='json')
def prepare_edit_project_view(request):
    try:
        data = request.json_body
        project_id = data.get("project_id")
        if not project_id:
            return {"success": False, "error": "Project ID is required."}

        request.session['edit_project_id'] = project_id
        print(f"[INFO] project_id {project_id} guardado en sesión.")
        return {"success": True}
    except Exception as e:
        print(f"[ERROR] Error al preparar proyecto para edición: {e}")
        return {"success": False, "error": str(e)}


@view_config(route_name='get_filtered_requests', renderer='json')
def get_filtered_requests(request):
    log.info(f"get_filtered_requests called with type_id={request.GET.get('type_id')}")
    try:
        type_id = int(request.GET.get('type_id', 3))

        # MAPEO PRIORIDADES
        priority_map = {
            p.id: p.priority
            for p in request.dbsession.query(TaskPriorities).all()
        }

        # TASKS CON REQUESTS
        tasks_query = (
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
        )
        dbtasks = tasks_query.all() if type_id != 1 else []

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

        # PROJECT REQUESTS (sin task_id)
        project_requests_query = (
            request.dbsession.query(Projects)
            .options(joinedload(Projects.requests))
            .filter(
                exists().where(
                    and_(
                        Requests.project_id == Projects.id,
                        Requests.task_id == None,
                        Requests.status_id == 1
                    )
                )
            )
        )
        dbprojects = project_requests_query.all() if type_id != 2 else []

        json_projects_with_requests = [{
            "id": proj.id,
            "name": proj.name,
            "start_date": proj.startdate.strftime('%Y-%m-%d') if proj.startdate else "N/A",
            "end_date": proj.enddate.strftime('%Y-%m-%d') if proj.enddate else "N/A",
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
                for req in sorted(proj.requests, key=lambda r: (
                    (1 if r.accepted_by or r.rejected_by else 0),
                    r.request_date or datetime.max
                ))
            ]
        } for proj in dbprojects]

        return {
            'tasks': json_tasks,
            'projects_requests': json_projects_with_requests
        }

    except Exception as e:
        print(f"[ERROR] get_filtered_requests: {e}")
        return {'error': str(e)}
