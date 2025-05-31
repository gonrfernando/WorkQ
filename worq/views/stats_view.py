from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from datetime import datetime
from worq.models.models import Projects, Tasks, UsersTasks, UsersProjects

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

    # Obtener todos los proyectos
    all_projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": p.id, "name": p.name} for p in all_projects]

    # Obtener el proyecto activo desde la sesión
    active_project_id = session.get("project_id")
    if not active_project_id and json_projects:
        active_project_id = json_projects[0]["id"]
        session["project_id"] = active_project_id

    active_project_id = int(active_project_id)
    active_project = next((p for p in json_projects if p["id"] == active_project_id), None)

    # Obtener tareas del usuario filtradas por proyecto activo
    usertasks_query = request.dbsession.query(Tasks).join(UsersTasks).filter(
        UsersTasks.user_id == user_id,
        Tasks.project_id == active_project_id
    )
    usertasks = usertasks_query.all()

    total_assigned = sum(1 for t in usertasks if t.status_id == 1)
    total_completed = sum(1 for t in usertasks if t.status_id == 3)
    total_late = sum(1 for t in usertasks if t.status_id == 2)

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
