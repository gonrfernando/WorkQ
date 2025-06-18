import datetime
from worq.models.models import UsersProjects, Roles, Users, Tasks, TaskRequirements, TaskPriorities, UsersTasks
from sqlalchemy.exc import SQLAlchemyError
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
import json

@view_config(
    route_name='add_task',
    renderer='worq:templates/add_task.jinja2',
    request_method=('GET', 'POST')
)
def task_creation_view(request):
    session = request.session
    if 'user_name' not in session:
        return HTTPFound(
            location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'})
        )
    if 'user_role' not in ['superadmin', 'admin', 'projectmanager']:
        return HTTPFound(
            location=request.route_url('task_view')
        )

    dbsession = request.dbsession
    active_project_id = session.get("project_id")
    user_id = session.get('user_id')

    # --- POST handling ---
    if request.method == 'POST':
        # Soporta tanto JSON como form-data
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
                    # Responde JSON si es petición AJAX
                    if 'application/json' in request.accept:
                        return Response(json.dumps({'success': True}), content_type='application/json; charset=utf-8')
                except SQLAlchemyError as e:
                    print(f"[ERROR] Error al asignar usuario: {e}")
                    if 'application/json' in request.accept:
                        return Response(json.dumps({'success': False, 'error': 'Error al editar el usuario'}), content_type='application/json; charset=utf-8')
                    return Response("Error al asignar usuario al proyecto", status=500)

        elif form_type == 'add_task':
            title         = get('title')
            description   = get('description')
            finished_date = get('finished_date')
            if finished_date:
                dt = datetime.datetime.strptime(finished_date, '%Y-%m-%dT%H:%M')
                if dt < datetime.datetime.utcnow():
                    return Response("The due date cant be in the past.", status=400)
            priority      = get('priority')
            requirements  = getall('requirements')
            collaborators = getall('collaborators')

            try:
                new_task = Tasks(
                    title=title,
                    description=description,
                    project_id=active_project_id,
                    creation_date=datetime.datetime.utcnow(),
                    finished_date=(
                        datetime.datetime.strptime(finished_date, '%Y-%m-%dT%H:%M')
                        if finished_date else None
                    ),
                    priority_id=int(priority) if priority else None,
                    status_id=4,
                    created_by=user_id
                )
                dbsession.add(new_task)
                dbsession.flush()

                # Guardar requisitos
                for req in requirements:
                    req_text = req.strip()
                    if req_text:
                        dbsession.add(TaskRequirements(
                            task_id=new_task.id,
                            requirement=req_text,
                            is_completed=False
                        ))

                for collab in collaborators:
                    collab_text = collab.strip().lower()
                    if not collab_text:
                        continue

                    user = dbsession.query(Users).filter(
                        Users.email.ilike(collab_text)
                    ).first()

                    if not user:
                        # Crear nuevo usuario con valores por defecto
                        user = Users(
                            name=collab_text.split('@')[0].capitalize(),
                            email=collab_text,
                            tel='',
                            country_id=None,
                            area_id=None,
                            role_id=None
                        )
                        dbsession.add(user)
                        dbsession.flush()  # para obtener user.id

                    dbsession.add(UsersTasks(
                        task_id=new_task.id,
                        user_id=user.id
                    ))

                dbsession.flush()
                print(f"[INFO] Tarea '{title}' creada con ID {new_task.id}")

                if 'application/json' in request.accept:
                    return Response(json.dumps({'success': True}), content_type='application/json; charset=utf-8')

            except SQLAlchemyError as e:
                print(f"[ERROR] Error al crear la tarea: {e}")
                if 'application/json' in request.accept:
                    return Response(json.dumps({'success': False, 'error': 'Error al crear la tarea'}), content_type='application/json; charset=utf-8')
                return Response("Error al crear la tarea", status=500)

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

    priorities = dbsession.query(TaskPriorities).all()
    json_priorities = [{"id": p.id, "priority": p.priority} for p in priorities]

    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M')

    proj_users = (
        dbsession.query(UsersProjects)
        .filter_by(project_id=active_project_id)
        .all()
    )
    json_proj_users = [
        {
            "id": up.user.id,
            "email": up.user.email,
            "name": up.user.name
        }
        for up in proj_users
    ]

    return {
        "users": json_users,
        "roles": json_roles,
        "projects": json_projects,
        "active_project_id": active_project_id,
        "active_project": active_project,
        "now": now,
        "priorities": json_priorities,
        "users_projects": json_proj_users,        
        "user_name": session.get('user_name'),
        "user_email": session.get('user_email'),
        "user_role": session.get('user_role'),
        "active_tab": "pm"
    }