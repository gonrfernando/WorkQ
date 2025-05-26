from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, TaskPriorities
from sqlalchemy.orm import joinedload
from pyramid.httpexceptions import HTTPFound

@view_config(route_name='task_view', renderer='worq:templates/task_view.jinja2')
def my_view(request):
    session = request.session
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    # 1) Proyectos disponibles
    projects = request.dbsession.query(Projects).all()

    # 2) Inicializar proyecto activo
    active_project_id = session.get("project_id")
    if not active_project_id and projects:
        active_project_id = projects[0].id
        session["project_id"] = active_project_id
    active_project_id = int(active_project_id) if active_project_id is not None else None

    # 3) Parámetros de sesión
    user_name  = session['user_name']
    user_email = session.get('user_email')
    user_role  = session.get('user_role')
    error      = request.params.get('error')

    # 4) Cargar prioridades desde la BD
    priority_map = {
        p.id: p.priority
        for p in request.dbsession.query(TaskPriorities).all()
    }

    # 5) Cargar tareas, precargando TaskRequirements y TaskPriorities
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

    # 6) Serializar a JSON
    json_projects = [{"id": p.id, "name": p.name} for p in projects]
    active_project = next((p for p in json_projects if p["id"] == active_project_id), None)

    json_tasks = []
    for task in dbtasks:
        json_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            # Usamos el mapa en caso de que la relación no esté cargada
            "priority": priority_map.get(task.priority_id, "None"),
            "due_date": task.finished_date,
            "requirements": [
                {
                    "id": req.id,
                    "requirement": req.requirement,
                    "is_completed": req.is_completed
                }
                for req in task.task_requirements
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
        "message": error
    }
