from pyramid.view import view_config
from worq.models.models import Projects
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError

from worq.models.models import Projects


@view_config(route_name='home', renderer='worq:templates/workq_main.jinja2')
def my_view(request):
    try:
        session = request.session
        if not 'user_name' in session:
            return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
        projects = request.dbsession.query(Projects).all()
        json_projects = [{"id": project.id, "name": project.name} for project in projects]
        active_project_id = session.get("project_id")
        user_name = session.get('user_name')
        user_email = session.get('user_email')
        user_role = session.get('user_role')
        return {
            "projects": json_projects,
            "active_project_id": active_project_id,
            'user_name': user_name,
            'user_email': user_email,
            'user_role': user_role
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPInternalServerError("An unexpected error occurred.")

@view_config(route_name='set_active_project', renderer='json')
def set_active_project(request):
    try:
        data = request.json_body
        project_id = data.get("project_id")
        if project_id:
            request.session["project_id"] = int(project_id)
            return {}
        return {}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPInternalServerError("An unexpected error occurred.")