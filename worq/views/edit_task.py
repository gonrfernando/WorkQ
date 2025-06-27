import datetime
import json

from worq.models.models import UsersProjects, Roles, Users, Tasks, TaskRequirements, TaskPriorities, UsersTasks
from sqlalchemy.exc import SQLAlchemyError
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from zope.sqlalchemy import ZopeTransactionEvents

@view_config(route_name='edit_task', renderer='worq:templates/edit_task.jinja2', request_method=('GET', 'POST'))
def task_edit_view(request):
    print("[INFO] Starting task edit view.")

    session = request.session
    if 'user_name' not in session:
        print("[WARNING] Unauthenticated user. Redirecting to sign in.")
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    if session.get('user_role') not in ('admin', 'superadmin'):
        print(f"[WARNING] Access denied. Current role: {session.get('user_role')}")
        return HTTPFound(location=request.route_url('task_view'))

    dbsession = request.dbsession
    active_project_id = session.get("project_id")
    user_id = session.get('user_id')

    # Get the task_id from POST, JSON or GET
    if request.method == 'POST':
        if request.content_type and 'application/json' in request.content_type:
            data = request.json_body
            task_id = data.get("task_id")
        else:
            data = request.POST
            task_id = data.get("task_id")
    else:
        # In GET, allow to get it by parameter or keep it in session if already loaded before
        task_id = request.params.get("task_id") or request.session.get("edit_task_id")

    if not task_id:
        print("[ERROR] No task ID provided.")
        return HTTPFound(location=request.route_url('task_view'))

    # Find the task without depending on the active project
    task = dbsession.query(Tasks).filter_by(id=task_id).first()
    if not task:
        print(f"[ERROR] Task not found (ID: {task_id}).")
        return HTTPFound(location=request.route_url('task_view'))

    if not task_id:
        print("[ERROR] No task ID provided.")
        return HTTPFound(location=request.route_url('task_view'))

    task = dbsession.query(Tasks).filter_by(id=task_id).first()
    if not task:
        print(f"[ERROR] Task not found (ID: {task_id}, Project: {active_project_id}).")
        return HTTPFound(location=request.route_url('task_view'))

    print(f"[INFO] Editing task ID: {task.id}")

    # --- POST ---
    if request.method == 'POST':
        print("[INFO] POST method detected. Processing data...")

        if request.content_type and 'application/json' in request.content_type:
            data = request.json_body
            get = data.get
            getall = lambda k: data[k] if isinstance(data.get(k), list) else [data[k]] if data.get(k) else []
            print("[INFO] Data received as JSON.")
        else:
            data = request.POST
            get = data.get
            getall = data.getall
            print("[INFO] Data received as POST form.")

        form_type = get('form_type')
        if form_type != 'edit_task':
            print("[WARNING] Invalid form type:", form_type)
            return Response(json.dumps({'success': False, 'error': 'Invalid form type'}), content_type='application/json; charset=utf-8')

        try:
            print("[INFO] Validating data...")

            title = get('title')
            description = get('description')
            if not title or not description:
                return Response(json.dumps({'success': False, 'error': 'Title and Description are required'}), content_type='application/json; charset=utf-8')

            # Update task
            task.title = title
            task.description = description
            finished_date = get('finished_date')
            task.finished_date = datetime.datetime.strptime(finished_date, '%Y-%m-%dT%H:%M') if finished_date else None
            task.priority_id = int(get('priority')) if get('priority') else None
            task.status_id = 4
            

            # Requirements
            dbsession.query(TaskRequirements).filter_by(task_id=task.id).delete()
            for req in getall('requirements'):
                req_text = req.strip()
                if req_text:
                    dbsession.add(TaskRequirements(task_id=task.id, requirement=req_text, is_completed=False))
            print("[INFO] Requirements updated.")

            # Collaborators
            dbsession.query(UsersTasks).filter_by(task_id=task.id).delete()
            new_collabs = []
            for collab in getall('collaborators'):
                collab_text = collab.strip().lower()
                if not collab_text:
                    continue
                user = dbsession.query(Users).filter(Users.email.ilike(collab_text)).first()
                if not user:
                    print(f"[INFO] New user detected, creating: {collab_text}")
                    user = Users(
                        name=collab_text.split('@')[0].capitalize(),
                        email=collab_text,
                        tel='',
                        country_id=None,
                        area_id=None,
                        role_id=None
                    )
                    dbsession.add(user)
                    dbsession.flush()
                new_collabs.append(UsersTasks(task_id=task.id, user_id=user.id))

            dbsession.add_all(new_collabs)

            dbsession.flush()
            print(f"[SUCCESS] Task successfully edited: ID {task.id}")

            # Clear the edited task ID to avoid reuse
            request.session.pop("edit_task_id", None)
            return Response(
                json.dumps({
                    'success': True,
                    'redirect': request.route_url('request_management')
                }),
                content_type='application/json; charset=utf-8'
            )



        except SQLAlchemyError as e:
            print(f"[ERROR] Error editing the task in the database: {e}")
            return Response(json.dumps({'success': False, 'error': 'Error editing the task'}), content_type='application/json; charset=utf-8')

    # --- GET: render template with task data ---
    print("[INFO] GET method detected. Preparing data for template.")
    users = dbsession.query(Users).all()
    json_users = [{"id": u.id, "name": u.name, "email": u.email, "tel": u.tel, "country_id": u.country_id, "area_id": u.area_id, "role_id": u.role_id} for u in users]

    roles = dbsession.query(Roles).all()
    json_roles = [{"id": r.id, "name": r.name} for r in roles]

    priorities = dbsession.query(TaskPriorities).filter(TaskPriorities.id != 4).all()
    json_priorities = [{"id": p.id, "priority": p.priority} for p in priorities]

    proj_users = dbsession.query(UsersProjects).filter_by(project_id=active_project_id).all()
    json_proj_users = [{"id": up.user.id, "email": up.user.email, "name": up.user.name} for up in proj_users]

    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority_id": task.priority_id,
        "finished_date": task.finished_date.strftime('%Y-%m-%dT%H:%M') if task.finished_date else '',
        "requirements": [r.requirement for r in task.task_requirements],
        "collaborators": [
            dbsession.query(Users).filter_by(id=ut.user_id).first().email
            for ut in task.users_tasks
        ]
    }

    print(f"[INFO] Data prepared for editing task ID {task.id}")

    response_data = {
        "users": json_users,
        "roles": json_roles,
        "priorities": json_priorities,
        "users_projects": json_proj_users,
        "user_name": session.get('user_name'),
        "user_email": session.get('user_email'),
        "user_role": session.get('user_role'),
        "active_project_id": active_project_id,
        "task_to_edit": task_data,
        "projects": []  # Adjust as needed
    }

    print("[DEBUG] Data returned when rendering template:")
    print(json.dumps(response_data, indent=2, default=str))

    return response_data

@view_config(route_name='delete_task_status', request_method='POST', renderer='json')
def delete_task_status(request):
    print("[DEBUG] delete_task_status: call received.")
    try:
        data = request.json_body
        task_id = data.get('task_id')
        user_id = request.session.get('user_id')

        if not task_id:
            return {'success': False, 'error': 'No task ID provided'}

        task = request.dbsession.query(Tasks).filter_by(id=task_id).first()

        if not task:
            return {'success': False, 'error': 'Task not found'}
        TASK_STATUS_DELETED = 7
        task.status_id = TASK_STATUS_DELETED
        request.dbsession.flush()
        print(f"[SUCCESS] Task deleted: ID {task.id}")
        print(f"New status_id: {task.status_id}") 

        return {
            'user_id': user_id,
            'success': True,
            'redirect': request.route_url('request_management')
        }

    except Exception as e:
        print(f"[ERROR] delete_task_status: {e}")
        return {'success': False, 'error': str(e)}
