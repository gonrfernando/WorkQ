import datetime
from worq.models.models import UsersProjects, Roles, Users, UsersTasks, Actions
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

    # Asegura que active_project_id sea int para comparación
    if active_project_id is not None:
        try:
            active_project_id = int(active_project_id)
        except ValueError:
            active_project_id = None

    # --- POST handling ---
    if request.method == 'POST':
        if request.content_type and 'application/json' in request.content_type:
            data = request.json_body
            get = data.get
            getall = lambda k: data[k] if isinstance(data.get(k), list) else [data[k]] if data.get(k) else []
        else:
            data = request.POST
            get = data.get
            getall = data.getall

        form_type = get('form_type')

        if form_type == 'add_user':
            user_id_selected = get('user_id')
            role_id_selected = get('role_id')
            if user_id_selected and active_project_id:
                try:
                    exists = dbsession.query(UsersProjects).filter_by(
                        user_id=user_id_selected,
                        project_id=active_project_id
                    ).first()
                    if not exists:
                        new_up = UsersProjects(
                            user_id=user_id_selected,
                            project_id=active_project_id,
                            role_id=role_id_selected,
                            invited_by=user_id
                        )
                        dbsession.add(new_up)
                        dbsession.flush()
                    if 'application/json' in request.accept:
                        return Response(json.dumps({'success': True}), content_type='application/json; charset=utf-8')
                except SQLAlchemyError as e:
                    print(f"[ERROR] Error al asignar usuario: {e}")
                    if 'application/json' in request.accept:
                        return Response(json.dumps({'success': False, 'error': 'Error al editar el usuario'}), content_type='application/json; charset=utf-8')
                    return Response("Error al asignar usuario al proyecto", status=500)

        # Si es AJAX y no hubo error, responde éxito genérico
        if 'application/json' in request.accept:
            return Response(json.dumps({'success': True}), content_type='application/json; charset=utf-8')

    # --- Datos para renderizado en GET y tras POST ---
    ups = dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
    json_projects = [
        {"id": up.project_id, "name": up.project.name}
        for up in ups
    ]
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
        "user_role": session.get('user_role')
    }