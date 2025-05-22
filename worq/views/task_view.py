from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, UsersProjects, Status
from pyramid.httpexceptions import HTTPFound


@view_config(route_name='task_view', renderer='worq:templates/task_view.jinja2')
def my_view(request):
    session = request.session

    # Validación de sesión
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')

    # 🔍 Obtener los proyectos del usuario a través de UsersProjects
    user_projects = (
        request.dbsession.query(Projects)
        .join(UsersProjects)
        .filter(UsersProjects.user_id == user_id)
        .all()
    )

    # Convertir a JSON para pasar a la plantilla
    json_projects = [{"id": project.id, "name": project.name} for project in user_projects]

    # Obtener proyecto activo
    active_project_id = session.get("project_id")
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)

    # Si no hay proyecto activo, asignar el primero (opcional)
    if not active_project and json_projects:
        active_project = json_projects[0]
        active_project_id = active_project["id"]

    # 📌 Obtener tareas del proyecto activo
    dbtasks = request.dbsession.query(Tasks).filter_by(project_id=active_project_id).all()
    priorities = {1: "Low", 2: "Avg", 3: "High"}

    json_tasks = [{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": priorities.get(task.priority, "None"),
        "due_date": task.finished_date.strftime('%Y-%m-%d %H:%M:%S') if task.finished_date else "N/A",
        "project_id": task.project_id, 
        "requirements": [
            {
                "id": req.id,
                "requirement": req.requirement,
                "is_completed": req.is_completed
            }
            for req in request.dbsession.query(TaskRequirements).filter_by(task_id=task.id).all()
        ]
    } for task in dbtasks]

    return {
        "projects": json_projects,
        "active_project": active_project,
        "tasks": json_tasks,
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "user_id": user_id
    }
