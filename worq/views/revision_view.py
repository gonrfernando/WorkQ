from pyramid.view import view_config
from worq.models.models import Projects

from pyramid.httpexceptions import HTTPFound
@view_config(route_name='revision_view', renderer='worq:templates/revision_view.jinja2')
def my_view(request):
    session = request.session
    error = request.params.get('error')
    if not 'user_name' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    error = request.params.get('error')
    if error:
            return {'message' : error }
    
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    active_project_id = 1
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    if user_role == "user" or user_role == "projectmanager" :
        return HTTPFound(location=request.route_url('task_view', _query={'error': 'Sorry, it looks like you don’t have permission to view this content.'}))
    return {
            "projects": json_projects,
            "active_project_id": active_project_id,
            'user_name': user_name,
            'user_email': user_email,
            'user_role': user_role,
            'message': error if error else None,
            'active_tab':"revision"
        }