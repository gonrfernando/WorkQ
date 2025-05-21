import datetime
from worq.models.models import UsersProjects, Roles, Users, Tasks, TaskRequirements
from sqlalchemy.exc import SQLAlchemyError
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

@view_config(route_name='add_task', renderer='worq:templates/add_task.jinja2', request_method=('GET', 'POST'))
def task_creation_view(request):
    session = request.session
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    dbsession = request.dbsession
    active_project_id = session.get("project_id")
    user_id = session.get('user_id')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'add_user':
                user_id_selected = request.POST.get('user_id')
                role_id_selected = request.POST.get('role_id')  # <-- Nuevo: obtener el rol
                if user_id_selected and active_project_id:
                    try:
                        exists = dbsession.query(UsersProjects).filter_by(
                            user_id=user_id_selected, project_id=active_project_id
                        ).first()
                        if not exists:
                            new_user_project = UsersProjects(
                                user_id=user_id_selected,
                                project_id=active_project_id,
                                role_id=role_id_selected  # <-- Nuevo: asignar rol
                            )
                            dbsession.add(new_user_project)
                            dbsession.flush()
                    except SQLAlchemyError as e:
                        print(f"[ERROR] Error al asignar usuario: {e}")
                        return Response("Error al asignar usuario al proyecto", status=500)


        elif form_type == 'add_task':
            title = request.POST.get('title')
            description = request.POST.get('description')
            finished_date = request.POST.get('finished_date')
            priority = request.POST.get('priority')
            requirements = request.POST.getall('requirements')

            try:
                new_task = Tasks(
                title=title,
                description=description,
                project_id=active_project_id,
                creation_date=datetime.datetime.utcnow(),
                finished_date=datetime.datetime.strptime(finished_date, '%Y-%m-%dT%H:%M') if finished_date else None,
                priority=int(priority) if priority else None
            )
                dbsession.add(new_task)
                dbsession.flush()  # Para obtener el ID generado

                for req in requirements:
                    if req.strip():
                        dbsession.add(TaskRequirements(
                            task_id=new_task.id,
                            requirement=req.strip(),
                            is_completed=False
                        ))

                dbsession.flush()
                print(f"[INFO] Tarea '{title}' creada con ID {new_task.id}")
            except Exception as e:
                print(f"[ERROR] Error al crear la tarea: {e}")
                return Response("Error al crear la tarea", status=500)

    # Datos para renderizado
    project_ids = dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
    json_projects = [{"id": p.project_id, "name": p.project.name} for p in project_ids]
    active_project = next((p for p in json_projects if p["id"] == active_project_id), None)

    users = dbsession.query(Users).all()
    roles = dbsession.query(Roles).all()
    json_users = [{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "tel": user.tel,
        "passw": user.passw,
        "country_id": user.country_id,
        "area_id": user.area_id,
        "role_id": user.role_id
    } for user in users]
    started_date_value = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    return {
        "users": json_users,
        "roles": [{"id": role.id, "name": role.name} for role in roles],
        "projects": json_projects,
        "active_project_id": active_project_id,
        "active_project": active_project,
        "started_date_value": started_date_value,
        'user_name': session.get('user_name'),
        'user_email': session.get('user_email'),
        'user_role': session.get('user_role')
    }


