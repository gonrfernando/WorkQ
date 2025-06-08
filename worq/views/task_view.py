from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, TaskPriorities, UsersProjects
from sqlalchemy.orm import joinedload
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.response import Response
from sqlalchemy.orm.exc import NoResultFound

@view_config(route_name='task_view', renderer='worq:templates/task_view.jinja2')
def task_view(request):
    session = request.session

    # Redirigir si el usuario no está autenticado
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    # Parámetros de sesión
    user_name  = session['user_name']
    user_email = session.get('user_email')
    user_role  = session.get('user_role')
    user_id    = session.get('user_id')  # Esto se necesita para filtrar proyectos
    error      = request.params.get('error')

    # 1) Obtener solo los proyectos del usuario
    user_projects = (
        request.dbsession.query(Projects)
        .join(UsersProjects)
        .filter(UsersProjects.user_id == user_id)
        .all()
    )

    json_projects = [{"id": project.id, "name": project.name} for project in user_projects]

    # 2) Determinar proyecto activo
    active_project_id = session.get("project_id")
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)

    if not active_project and json_projects:
        active_project = json_projects[0]
        active_project_id = active_project["id"]
        session["project_id"] = active_project_id

    active_project_id = int(active_project_id) if active_project_id is not None else None

    # 3) Cargar prioridades desde la base de datos
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
            joinedload(Tasks.priority),
            joinedload(Tasks.users)
        )
        .filter_by(project_id=active_project_id)
        .order_by(Tasks.priority_id.desc())
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
            ],
            "assigned_users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
            for user in (task.users or [])
            ]
        })

    return {
        "projects": json_projects,
        "active_project": active_project,
        "tasks": json_tasks,
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "active_tab": "tasks",
        "message": error if error else None  # Agrega 'message' solo si 'error' tiene un valor
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