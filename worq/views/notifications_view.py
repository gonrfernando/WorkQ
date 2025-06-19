import datetime
from worq.models.models import UsersProjects, Projects, Notifications, ProjectNotifications, UsersNotifications, Types
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
import json

@view_config(route_name='noti_view', renderer='worq:templates/noti_view.jinja2')
def noti_view(request):
    session = request.session
    if 'user_name' not in session:
        return HTTPFound(
            location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'})
        )

    dbsession = request.dbsession
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    # 1. Obtener proyectos donde participa el usuario
    if user_role in ['superadmin', 'admin']:
        user_projects = (
            dbsession.query(Projects)
            .filter(Projects.state_id != 2)
            .all()
        )
    else:
        user_projects = (
            dbsession.query(Projects)
            .join(UsersProjects)
            .filter(
                UsersProjects.user_id == user_id,
                Projects.state_id != 2
            )
            .all()
        )

    project_ids = [p.id for p in user_projects]
    json_projects = [{"id": p.id, "name": p.name} for p in user_projects]

    # 2. Obtener notificaciones relacionadas a esos proyectos y al usuario
    notifications = (
        dbsession.query(Notifications, ProjectNotifications, Types, Projects)
        .join(ProjectNotifications, ProjectNotifications.noti_id == Notifications.id)
        .join(Projects, Projects.id == ProjectNotifications.project_id)
        .join(Types, Types.id == Notifications.type_id)
        .join(UsersNotifications, UsersNotifications.noti_id == Notifications.id)
        .filter(
            ProjectNotifications.project_id.in_(project_ids),
            UsersNotifications.user_id == user_id
        )
        .order_by(Notifications.date.desc())
        .all()
    )

    # 3. Formatear notificaciones para la plantilla
    notifications_list = []
    for notif, proj_notif, notif_type, project in notifications:
        notifications_list.append({
            "id": notif.id,
            "type": notif_type.type,
            "project_name": project.name,
            "date": notif.date,
            "state": notif.state,
            "type_id": notif.type_id
        })
    print("user_id:", user_id)
    print("user_role:", user_role)
    print("project_ids:", project_ids)
    print("Total notificaciones encontradas:", len(notifications))
    for notif, proj_notif, notif_type, project in notifications:
        print("Notificación:", notif.id, notif_type.type, project.name, notif.state)
    return {
        "notifications": notifications_list,
        "projects": json_projects,
        "user_name": session.get('user_name'),
        "user_email": session.get('user_email'),
        "user_role": session.get('user_role'),
        "active_tab": "actions"
    }