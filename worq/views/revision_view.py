from pyramid.view import view_config
from worq.models.models import Projects, Tasks, TaskRequirements, TaskPriorities, UsersProjects, Users, Feedbacks
from sqlalchemy.orm import joinedload
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from sqlalchemy import and_
from datetime import datetime

from pyramid.httpexceptions import HTTPFound
@view_config(route_name='revision_view', renderer='worq:templates/revision_view.jinja2')
def my_view(request):
    session = request.session
    error = request.params.get('error')
    if not 'user_email' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    error = request.params.get('error')
    if error:
            return {'message' : error }
    user_name  = session['user_name']
    user_email = session.get('user_email')
    user_role  = session.get('user_role')
    user_id    = session.get('user_id')  
    error      = request.params.get('error')
    
    if user_role == "user" :
        return HTTPFound(location=request.route_url('task_view', _query={'error': 'Sorry, it looks like you don’t have permission to view this content.'}))

    # 1) Obtener proyectos según rol del usuario
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

    # ... el resto de tu código sigue igual

    # 2) Determinar proyecto activo
    active_project_id = session.get("project_id")
    active_project = next((project for project in json_projects if project["id"] == active_project_id), None)

    if not active_project and json_projects:
        active_project = json_projects[0]
        active_project_id = active_project["id"]
        session["project_id"] = active_project_id

    active_project_id = int(active_project_id) if active_project_id is not None else None

    # 3) Cargar prioridades desde la base de datos
    priority_map = {
        p.id: p.priority
        for p in request.dbsession.query(TaskPriorities).all()
    }

    # 4) Consultar tareas con relaciones precargadas
    dbtasks = (
        request.dbsession
        .query(Tasks)
        .options(
            joinedload(Tasks.task_requirements),
            joinedload(Tasks.priority)
        )
        .filter(
            and_(
                Tasks.project_id == active_project_id,
                Tasks.status_id != 4,
                Tasks.status_id != 5,
                Tasks.status_id != 7,
                Tasks.status_id != 8
            )
        )
        .all()
    )

    # 5) Serializar tareas
    json_tasks = []
    for task in dbtasks:
        task_feedbacks = (
            request.dbsession.query(Feedbacks)
            .filter(Feedbacks.task_id == task.id)
            .order_by(Feedbacks.date.desc())
            .all()
        )

        feedback_list = [
            {
                "user_id": feedback.user_id,
                "user_name": feedback.user.name if feedback.user else "Unknown",
                "comment": feedback.comment,
                "date": feedback.date.strftime("%Y-%m-%d %H:%M") if feedback.date else ""
            }
            for feedback in task_feedbacks
        ]

        json_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": priority_map.get(task.priority_id, "None"),
            "due_date": task.finished_date.strftime('%Y-%m-%d %H:%M:%S') if task.finished_date else "N/A",
            "project_id": task.project_id,
            "requirements": [
                {
                    "id": req.id,
                    "requirement": req.requirement,
                    "is_completed": req.is_completed
                }
                for req in task.task_requirements
            ],
            "feedbacks": feedback_list
        })

    # 6) Cargar usuarios del proyecto activo
    users = (
        request.dbsession.query(Users)
        .join(UsersProjects, Users.id == UsersProjects.user_id)
        .filter(UsersProjects.project_id == active_project_id)
        .all()
    )

    return {
        "projects": json_projects,
        "active_project": active_project,
        "tasks": json_tasks,
        "user_name": user_name,
        "user_email": user_email,
        "user_role": user_role,
        "active_tab": "tasks",
        'message': error if error else None,
        "users": users,
        "active_project_id": active_project_id,
        'active_tab':"revision",
        "current_user_id": user_id,
    }

@view_config(route_name='save_feedback', renderer='json', request_method='POST')
def save_feedback(request):
    data = request.json_body
    user_id = request.session.get('user_id')

    if not user_id:
        return {"success": False, "error": "Usuario no autenticado"}

    user = request.dbsession.query(Users).filter_by(id=user_id).first()
    if not user:
        return {"success": False, "error": "Usuario no encontrado"}

    feedback_id = data.get("feedback_id")
    comment = data.get("comment")
    task_id_raw = data.get("task_id")

    if not comment or task_id_raw is None:
        return {"success": False, "error": "Faltan datos."}

    try:
        task_id = int(task_id_raw)
    except (ValueError, TypeError):
        return {"success": False, "error": "ID de tarea inválido."}

    task = request.dbsession.query(Tasks).filter_by(id=task_id).first()
    if not task:
        return {"success": False, "error": "Tarea no encontrada."}

    try:
        if feedback_id:
            # Actualizar feedback existente del usuario
            feedback = (
                request.dbsession.query(Feedbacks)
                .filter_by(id=feedback_id, user_id=user.id)
                .first()
            )
            if feedback:
                feedback.comment = comment
                feedback.date = datetime.utcnow()
            else:
                return {"success": False, "error": "Feedback no encontrado o no autorizado"}
        else:
            # Verificar si ya existe feedback del usuario para esta tarea
            feedback = (
                request.dbsession.query(Feedbacks)
                .filter_by(task_id=task_id, user_id=user.id)
                .first()
            )
            if feedback:
                # Actualizar si ya existe
                feedback.comment = comment
                feedback.date = datetime.utcnow()
            else:
                # Crear nuevo feedback
                feedback = Feedbacks(
                    user_id=user.id,
                    task_id=task_id,
                    comment=comment,
                    date=datetime.utcnow()
                )
                request.dbsession.add(feedback)

        request.dbsession.flush()  # para obtener id y datos actualizados

        # Devolver el último feedback guardado para este usuario y tarea
        latest_feedback = {
            "feedback_id": feedback.id,
            "user_id": feedback.user_id,
            "user_name": user.name,
            "comment": feedback.comment,
            "date": feedback.date.strftime("%Y-%m-%d %H:%M")
        }

        return {"success": True, "feedback": latest_feedback}

    except Exception as e:
        request.dbsession.rollback()
        return {"success": False, "error": f"Error interno: {str(e)}"}

@view_config(route_name='update_task_status', renderer='json', request_method='POST')
def update_task_status(request):
    try:
        data = request.json_body
        task_id = data.get('task_id')
        status_id = data.get('status_id')

        if not task_id or not status_id:
            return {"success": False, "error": "Missing task_id or status_id"}

        task = request.dbsession.query(Tasks).filter_by(id=task_id).first()
        if not task:
            return {"success": False, "error": "Task not found"}

        task.status_id = status_id
        request.dbsession.flush()  # Guardar en la DB

        return {"success": True}
    except Exception as e:
        request.dbsession.rollback()
        return {"success": False, "error": f"Internal error: {str(e)}"}
