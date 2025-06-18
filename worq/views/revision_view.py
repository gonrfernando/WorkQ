from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, TaskPriorities, UsersProjects, Users
from sqlalchemy.orm import joinedload
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import and_

from pyramid.httpexceptions import HTTPFound
@view_config(route_name='revision_view', renderer='worq:templates/revision_view.jinja2')
def my_view(request):
    session = request.session
    error = request.params.get('error')
    if not 'user_name' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    error = request.params.get('error')
    if error:
            return {'message' : error }
    user_name  = session['user_name']
    user_email = session.get('user_email')
    user_role  = session.get('user_role')
    user_id    = session.get('user_id')  
    error      = request.params.get('error')
    
    if user_role == "user" :
        return HTTPFound(location=request.route_url('task_view', _query={'error': 'Sorry, it looks like you don’t have permission to view this content.'}))

    # 1) Obtener proyectos según rol del usuario
    if user_role in ['superadmin', 'admin']:
        user_projects = (
            request.dbsession.query(Projects)
            .filter(Projects.state_id != 2)  # Filtrar los que no tienen state_id=2
            .all()
        )
    else:
        user_projects = (
            request.dbsession.query(Projects)
            .join(UsersProjects)
            .filter(
                UsersProjects.user_id == user_id,
                Projects.state_id != 2  # Filtrar también aquí
            )
            .all()
        )

    json_projects = [{"id": project.id, "name": project.name} for project in user_projects]

    # ... el resto de tu código sigue igual

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
            joinedload(Tasks.priority)
        )
        .filter(
            and_(
                Tasks.project_id == active_project_id,
                Tasks.status_id != 4,
                Tasks.status_id != 5,
                Tasks.status_id != 7  
            )
        )
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
        .join(UsersProjects, Users.id == UsersProjects.user_id)
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
        'message': error if error else None,
        "users": users,
        "active_project_id": active_project_id,
        'active_tab':"revision"
    }