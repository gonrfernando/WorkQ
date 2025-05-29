from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
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

    # Obtener proyectos
    all_projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": p.id, "name": p.name} for p in all_projects]

    # Obtener el proyecto activo
    active_project_id = request.params.get("project_id")
    try:
        active_project_id = int(active_project_id) if active_project_id else None
    except ValueError:
        active_project_id = 1

    # Obtener tareas del usuario
    usertasks_query = request.dbsession.query(Tasks).join(UsersTasks).filter(UsersTasks.user_id == user_id)
    if active_project_id:
        usertasks_query = usertasks_query.filter(Tasks.project_id == active_project_id)
    usertasks = usertasks_query.all()
    

    json_user_tasks = [{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "priority": t.priority,
        "finished_date": t.finished_date,
        "status_id": t.status_id,
        "project_id": t.project_id
    } for t in usertasks]

    # Obtener proyectos del usuario
    user_projects = request.dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
    json_user_projects = []
    for up in user_projects:
        if up.project:
            json_user_projects.append({
                "id": up.project_id,
                "name": up.project.name
            })

    return {
        "projects": json_projects,
        "active_project_id": active_project_id,
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "message": error if error else None,
        "active_tab": "stats",
        "usertasks": json_user_tasks,
        "userprojects": json_user_projects
    }
