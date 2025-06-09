from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, TaskPriorities, UsersProjects, Users
from sqlalchemy.orm import joinedload
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound

@view_config(route_name='task_view', renderer='worq:templates/task_view.jinja2')
def my_view(request):
    session = request.session
    projects = request.dbsession.query(Projects).all()
    if not 'user_name' in session:
            return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    error = request.params.get('error')
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    active_project_id = session.get("project_id")
    if not active_project_id and projects:
        # Fallback to first project if not set
        active_project_id = projects[0].id
        session["project_id"] = active_project_id
    if active_project_id is not None:
        active_project_id = int(active_project_id)
    
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)
    
    dbtasks = request.dbsession.query(Tasks).filter_by(project_id = active_project_id).all()
    priority_map = {
        p.id: p.priority
        for p in request.dbsession.query(TaskPriorities).all()
    }

    # 4) Consultar tareas con relaciones precargadas
    dbtasks = (
        request.dbsession
        .query(Tasks)
        .options(
            joinedload(Tasks.task_requirements),
            joinedload(Tasks.priority)
        )
        .filter_by(project_id=active_project_id)
        .all()
    )

    # 5) Serializar tareas
    json_tasks = []
    for task in dbtasks:
        json_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": priority_map.get(task.priority_id, "None"),
            "due_date": task.finished_date.strftime('%Y-%m-%d %H:%M:%S') if task.finished_date else "N/A",
            "project_id": task.project_id,
            "requirements": [
                {
                    "id": req.id,
                    "requirement": req.requirement,
                    "is_completed": req.is_completed
                }
                for req in task.task_requirements
            ]
        })

    # 6) Cargar usuarios del proyecto activo
    users = (
        request.dbsession.query(Users)
        .join(UsersProjects)
        .filter(UsersProjects.project_id == active_project_id)
        .all()
    )

    return {
        "projects": json_projects,
        "active_project": active_project,
        "tasks": json_tasks,
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "active_tab": "tasks",
        "message": error,
        "users": users,
        "active_project_id": active_project_id,
    }


@view_config(route_name='update_requirement', renderer='json', request_method='POST')
def update_requirement(request):
    try:
        data = request.json_body
        req_id = data.get("requirement_id")
        is_completed = data.get("is_completed")
        if req_id is None or is_completed is None:
            return {"success": False, "error": "Missing data"}
        req = request.dbsession.query(TaskRequirements).filter_by(id=req_id).one_or_none()
        if not req:
            return {"success": False, "error": "Requirement not found"}
        req.is_completed = bool(is_completed)
        request.dbsession.flush()
        return {"success": True}
    except Exception as e:
        print(f"Error updating requirement: {e}")
        return {"success": False, "error": str(e)}