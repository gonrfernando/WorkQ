import datetime
from worq.models.models import UsersProjects, Roles, Users, UsersTasks, Actions, Projects
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
import json

@view_config(route_name='action_view', renderer='worq:templates/action_view.jinja2')
def action_view(request):
    session = request.session
    if 'user_name' not in session:
        return HTTPFound(
            location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'})
        )
    dbsession = request.dbsession
    active_project_id = session.get("project_id")
    user_id = session.get('user_id')
    error = request.params.get('error')
    if not 'user_email' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    error = request.params.get('error')
    if error:
            return {'message' : error }
    
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    if not active_project_id:
        # Si no hay parámetro, usa el de sesión o el primero de la lista
        active_project_id = session.get("project_id") or (json_projects[0]["id"] if json_projects else None)
    else:
        active_project_id = int(active_project_id)
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')

    if user_role == "user" or user_role == "projectmanager":
        return HTTPFound(location=request.route_url('task_view', _query={'error': 'Sorry, it looks like you don’t have permission to view this content.'}))
    dbsession = request.dbsession
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
    active_project = next(
        (p for p in json_projects if p["id"] == active_project_id),
        None
    )

    users = dbsession.query(Users).all()
    json_users = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "tel": u.tel,
            "country_id": u.country_id,
            "area_id": u.area_id,
            "role_id": u.role_id
        }
        for u in users
    ]
    roles = dbsession.query(Roles).all()
    json_roles = [{"id": r.id, "name": r.name} for r in roles]

    proj_users = (
        dbsession.query(UsersProjects)
        .filter_by(project_id=active_project_id)
        .all()
    )
    filtered_users = [
    {
        "id": up.user.id,
        "name": up.user.name,
        "email": up.user.email,
        "role_id": up.user.role_id
    }
    for up in proj_users if up.user.role_id != 4
    ]
    json_proj_users = [
        {
        "id": up.user.id,
        "name": up.user.name,
        "email": up.user.email,
        "role_id": up.user.role_id
    }
    for up in proj_users if up.user.role_id != 4
    ]

    # --- Buscar acciones del proyecto activo ---
    actions = []
    if active_project_id:
        actions_query = (
            dbsession.query(Actions)
            .options(joinedload(Actions.type), joinedload(Actions.user))
            .filter(Actions.project_id == active_project_id)
            .order_by(Actions.date.desc())
            .all()
        )
        for action in actions_query:
            actions.append({
                "id": action.id,
                "type": action.type.type if action.type else "Sin tipo",
                "user": action.user.name if action.user else "Sin usuario",
                "timestamp": action.date
            })
    
    return {
        "users": filtered_users,
        "roles": json_roles,
        "projects": json_projects,
        "active_project_id": active_project_id,
        "active_project": active_project,
        "users_projects": json_proj_users,
        "actions": actions,
        "user_name": session.get('user_name'),
        "user_email": session.get('user_email'),
        "user_role": session.get('user_role'),
        "active_tab": "actions"
    }