from pyramid.view import view_config
from datetime import datetime
from worq.models.models import Requests
from pyramid.httpexceptions import HTTPFound

@view_config(route_name='submit_request', request_method='POST', renderer='json')
def submit_request(request):
    try:
        task_id_str = request.POST.get('task_id')
        action_type = request.POST.get('action_type')
        reason = request.POST.get('reason')

        user_id = request.session.get('user_id')
        project_id = request.session.get('project_id')

        # Requisitos mínimos
        if not all([task_id_str, action_type, reason, user_id, project_id]):
            return {"success": False, "error": "Please complete all required fields."}

        task_id = int(task_id_str)
        status_id = 1  # Pending by default

        new_request = Requests(
            user_id=user_id,
            project_id=project_id,
            status_id=status_id,
            action_type=action_type,
            reason=reason,
            request_date=datetime.now(),
            task_id=task_id
        )

        request.dbsession.add(new_request)
        request.dbsession.flush()

        return {"success": True}

    except Exception as e:
        print(f"[submit_request error] {e}")
        return {"success": False, "error": "An error occurred while submitting your request. Please try again later."}

@view_config(route_name='submit_request_project', request_method='POST', renderer='json')
def submit_request_project(request):
    try:
        action_type = request.POST.get('action_type')
        reason = request.POST.get('reason')

        user_id = request.session.get('user_id')

        project_id = request.POST.get('project_id')

        status_id = 1  # Pending by default

        # Mostrar valores para depuración
        print(f"user_id: {user_id}")
        print(f"project_id: {project_id}")
        print(f"action_type: {action_type}")
        print(f"reason: {reason}")

        new_request = Requests(
            user_id=user_id,
            project_id=project_id,
            status_id=status_id,
            action_type=action_type,
            reason=reason,
            request_date=datetime.now(),
        )

        request.dbsession.add(new_request)
        request.dbsession.flush()

        return HTTPFound(location=request.route_url('task_view'))

    except Exception as e:
        print(f"[submit_request error] {e}")
        return {"success": False, "error": "An error occurred while submitting your request. Please try again later."}
