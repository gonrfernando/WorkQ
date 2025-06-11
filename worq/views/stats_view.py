from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from datetime import datetime
from worq.models.models import Projects, Tasks, UsersTasks, UsersProjects
from sqlalchemy.orm import joinedload

@view_config(route_name='stats_view', renderer='worq:templates/stats_view.jinja2')
def stats_view(request):
    session = request.session
    error = request.params.get('error')
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')

    if not user_id:
        return HTTPFound(location=request.route_url('login'))

    # Obtener todos los proyectos del usuario
    user_projects = (
        request.dbsession.query(Projects)
        .join(UsersProjects)
        .filter(UsersProjects.user_id == user_id)
        .all()
    )

    json_projects = [{"id": project.id, "name": project.name} for project in user_projects]

    # Obtener el proyecto activo desde la sesión o asignar el primero
    active_project_id = session.get("project_id")
    if not active_project_id and json_projects:
        active_project_id = json_projects[0]["id"]
        session["project_id"] = active_project_id

    active_project_id = int(active_project_id)
    active_project = next((p for p in json_projects if p["id"] == active_project_id), None)

    # Base query para tareas del proyecto activo
    query = (
        request.dbsession
        .query(Tasks)
        .options(
            joinedload(Tasks.task_requirements),
            joinedload(Tasks.priority),
            joinedload(Tasks.users)
        )
        .filter(Tasks.project_id == active_project_id)
    )

    # Filtrar por usuario si es user
    if user_role == "user":
        query = query.join(UsersTasks).filter(UsersTasks.user_id == user_id)

    dbtasks = query.order_by(Tasks.priority_id.desc()).all()

    # 📌 Calcular estadísticas basadas en tareas filtradas
    total_assigned = sum(1 for t in dbtasks if t.status_id == 1)
    total_completed = sum(1 for t in dbtasks if t.status_id == 3)
    total_late = sum(1 for t in dbtasks if t.status_id == 2)

    return {
        "projects": json_projects,
        "active_project": active_project,
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "message": error if error else None,
        "active_tab": "stats",
        "stats": {
            "assigned": total_assigned,
            "completed": total_completed,
            "late": total_late
        }
    }
