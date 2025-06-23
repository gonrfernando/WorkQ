import datetime
import json
from sqlalchemy.exc import SQLAlchemyError
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from worq.models.models import Projects


@view_config(route_name='edit_project', renderer='worq:templates/edit_project.jinja2', request_method=('GET', 'POST'))
def edit_project_view(request):
    print("[INFO] Starting project edit view.")

    session = request.session
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    if session.get('user_role') not in ('admin', 'superadmin'):
        print(f"[WARNING] Access denied. Current role: {session.get('user_role')}")
        return HTTPFound(location=request.route_url('task_view'))

    dbsession = request.dbsession

    # Get project_id
    if request.method == 'POST':
        if request.content_type and 'application/json' in request.content_type:
            data = request.json_body
            project_id = data.get("project_id")
        else:
            data = request.POST
            project_id = data.get("project_id")
    else:
        project_id = session.get("edit_project_id")

    if not project_id:
        print("[ERROR] No project_id provided.")
        return HTTPFound(location=request.route_url('task_view'))

    project = dbsession.query(Projects).filter_by(id=project_id).first()
    if not project:
        print(f"[ERROR] Project not found. ID: {project_id}")
        return HTTPFound(location=request.route_url('task_view'))

    print(f"[INFO] Project found. ID: {project.id}")

    # --- POST: Update project ---
    if request.method == 'POST':
        if request.content_type and 'application/json' in request.content_type:
            data = request.json_body
            get = data.get
            print("[INFO] JSON data received for editing.")
        else:
            data = request.POST
            get = data.get
            print("[INFO] POST data received for editing.")

        form_type = get('form_type')
        if form_type != 'edit_project':
            return Response(json.dumps({'success': False, 'error': 'Invalid form type'}), content_type='application/json', charset='utf-8')

        try:
            name = get('name')
            startdate = get('startdate')
            enddate = get('enddate')

            if not name or not startdate or not enddate:
                return Response(json.dumps({'success': False, 'error': 'Name, Start Date and End Date are required'}), content_type='application/json',charset='utf-8')

            # Update values
            project.name = name
            project.startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
            project.enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d").date()

            dbsession.flush()
            print(f"[SUCCESS] Project updated successfully: ID {project.id}")
            session.pop("edit_project_id", None)

            return Response(json.dumps({
                'success': True,
                'redirect': request.route_url('task_view')
            }).encode('utf-8'),  # encode to bytes
            content_type='application/json; charset=utf-8')

        except SQLAlchemyError as e:
            print(f"[ERROR] Database error: {e}")
            return Response(json.dumps({'success': False, 'error': 'Database error'}), content_type='application/json',charset='utf-8')

    # --- GET: Render template with project data ---
    project_data = {
        "id": project.id,
        "name": project.name,
        "startdate": project.startdate.strftime("%Y-%m-%d"),
        "enddate": project.enddate.strftime("%Y-%m-%d")
    }

    print(f"[INFO] Project data sent to template: {project_data}")

    return {
        "user_name": session.get('user_name'),
        "user_role": session.get('user_role'),
        "project": project_data,
        "projects": [] 
    }

@view_config(route_name='delete_project_status', request_method='POST', renderer='json')
def delete_project_status(request):
    print("[DEBUG] delete_project_status: request received.")

    try:
        data = request.json_body
        project_id = data.get('project_id')
        user_id = request.session.get('user_id')

        if not project_id:
            return {'success': False, 'error': 'No project ID provided'}

        project = request.dbsession.query(Projects).filter_by(id=project_id).first()

        if not project:
            return {'success': False, 'error': 'Project not found'}

        PROJECT_STATE_DELETED = 2  # Adjust if you use another ID for "deleted"
        project.state_id = PROJECT_STATE_DELETED

        request.dbsession.flush()
        print(f"[SUCCESS] Project marked as deleted: ID {project.id} (state_id={PROJECT_STATE_DELETED})")

        return {
            'user_id': user_id,
            'success': True,
            'redirect': request.route_url('task_view')
        }

    except Exception as e:
        print(f"[ERROR] delete_project_status: {e}")
        return {'success': False, 'error': str(e)}
