import datetime
from worq.models.models import UsersProjects, Roles, Users, Tasks, TaskRequirements, TaskPriorities, UsersTasks, Projects, Notifications, UsersNotifications, ProjectNotifications, Types
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
    user_email = session.get('user_email')
    user_role  = session.get('user_role')
    user_id    = session.get('user_id')
    if 'user_name' not in session:
        return HTTPFound(
            location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'})
        )
    if user_role not in ['superadmin', 'admin', 'projectmanager']:
        return HTTPFound(
            location=request.route_url('task_view')
        )
    
    dbsession = request.dbsession
    active_project_id = session.get("project_id")
    user_id = session.get('user_id')

    # --- POST handling ---
    if request.method == 'POST':
        active_project_id = request.POST.get("project_id")
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
        print("POST recibido")
        print("Content-Type:", request.content_type)
        print("Datos recibidos:", data)
        print("form_type:", form_type)
        if form_type == 'add_user':
            user_id_selected = get('user_id')
            user_email = get('email')
            # Elimina el uso de role_id_selected
            if not user_id_selected and user_email:
                user = dbsession.query(Users).filter(Users.email.ilike(user_email)).first()
                if user:
                    user_id_selected = user.id
                    print("user_id_selected:", user_id_selected)
                    if not user_id_selected:
                        return Response(json.dumps({'success': False, 'error': 'User is required'}), content_type='application/json; charset=utf-8')
                    print("user_id_selected:", user_id_selected)
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
                            invited_by=user_id
                        )
                        dbsession.add(new_up)
                        dbsession.flush()

                        try:
                            notif = Notifications(
                                type_id=9,  # ID fijo para "Usuario agregado a proyecto"
                                date=datetime.datetime.utcnow(),
                                state_id=4
                            )
                            dbsession.add(notif)
                            dbsession.flush()
                            dbsession.add(ProjectNotifications(
                                project_id=active_project_id,
                                noti_id=notif.id
                            ))
                            dbsession.add(UsersNotifications(
                                noti_id=notif.id,
                                user_id=user_id_selected
                            ))
                            dbsession.flush()
                        except Exception as e:
                            print(f"[ERROR] Al crear notificación de usuario agregado a proyecto: {e}")
                        if 'application/json' in request.accept:
                            return Response(json.dumps({'success': True}), content_type='application/json; charset=utf-8')
                    else:
                        # Usuario ya estaba en el proyecto, responde igual con éxito
                            if 'application/json' in request.accept:
                                return Response(json.dumps({'success': True, 'info': 'User already in project'}), content_type='application/json; charset=utf-8')
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
            print("title:", title, "description:", description, "priority:", priority)
            print("requirements:", requirements)
            print("collaborators:", collaborators)

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
                try:
                    notif = Notifications(
                        type_id=10,  # ID para "Tarea asignada"
                        date=datetime.datetime.utcnow(),
                        state_id=4  # Estado "Pendiente"
                    )
                    dbsession.add(notif)
                    dbsession.flush()
                    dbsession.add(ProjectNotifications(
                        project_id=active_project_id,
                        noti_id=notif.id
                    ))
                    for collab_email in collaborators:
                        collab_email = collab_email.strip().lower()
                        if not collab_email:
                            continue
                        user = dbsession.query(Users).filter(Users.email.ilike(collab_email)).first()
                        if user:
                            dbsession.add(UsersNotifications(
                                noti_id=notif.id,
                                user_id=user.id
                            ))
                    dbsession.flush()
                except Exception as e:
                    print(f"[ERROR] Al crear notificación de tarea asignada: {e}")
                    # Notificar a cada colaborador
                    for collab in collaborators:
                        collab_text = collab.strip().lower()
                        if not collab_text:
                            continue
                        user = dbsession.query(Users).filter(Users.email.ilike(collab_text)).first()
                        if user:
                            dbsession.add(UsersNotifications(
                                noti_id=notif.id,
                                user_id=user.id
                            ))
                    dbsession.flush()
                except Exception as e:
                    print(f"[ERROR] Al crear notificación de tarea asignada: {e}")
                dbsession.flush()
                print(f"[INFO] Tarea '{title}' creada con ID {new_task.id}")

                if 'application/json' in request.accept:
                    return Response(json.dumps({'success': True}), content_type='application/json; charset=utf-8')

            except SQLAlchemyError as e:
                print(f"[ERROR] Error al crear la tarea: {e}")
                if 'application/json' in request.accept:
                    return Response(json.dumps({'success': False, 'error': 'Error al crear la tarea'}), content_type='application/json; charset=utf-8')
                return Response("Error al crear la tarea", status=500)

        elif form_type == 'remove_user':
            user_id_selected = get('user_id')
            if not user_id_selected or not active_project_id:
                return Response(json.dumps({'success': False, 'error': 'User or project not specified'}), content_type='application/json; charset=utf-8')
            try:
                up = dbsession.query(UsersProjects).filter_by(
                    user_id=user_id_selected,
                    project_id=active_project_id
                ).first()
                if up:
                    dbsession.delete(up)
                    dbsession.flush()
                    if 'application/json' in request.accept:
                        return Response(json.dumps({'success': True}), content_type='application/json; charset=utf-8')
                else:
                    if 'application/json' in request.accept:
                        return Response(json.dumps({'success': False, 'error': 'User not found in project'}), content_type='application/json; charset=utf-8')
            except SQLAlchemyError as e:
                print(f"[ERROR] Error al eliminar usuario del proyecto: {e}")
                if 'application/json' in request.accept:
                    return Response(json.dumps({'success': False, 'error': 'Error al eliminar usuario del proyecto'}), content_type='application/json; charset=utf-8')
                return Response("Error al eliminar usuario del proyecto", status=500)
        # Si es AJAX y no hubo error, responde éxito genérico
        
            
    # --- Datos para renderizado en GET y tras POST ---
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
        }
        for u in users
    ]

    priorities = dbsession.query(TaskPriorities).filter(TaskPriorities.id != 4).all()
    json_priorities = [{"id": p.id, "priority": p.priority} for p in priorities]

    now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M')

    proj_users = (
        dbsession.query(UsersProjects)
        .join(Projects, UsersProjects.project_id == Projects.id)
        .filter(
            UsersProjects.project_id == active_project_id,
            Projects.state_id != 2
        )
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
        "projects": json_projects,
        "active_project_id": active_project_id,
        "active_project": active_project,
        "now": now,
        "priorities": json_priorities,
        "users_projects": json_proj_users,        
        "user_name": session.get('user_name'),
        "user_email": session.get('user_email'),
        "user_role": session.get('user_role'),
        "active_tab": "tasks"
    }