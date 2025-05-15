from pyramid.view import view_config
from worq.models.models import Projects
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPInternalServerError, HTTPBadRequest

from worq.models.models import Projects, Users, UsersProjects


@view_config(route_name='home', renderer='worq:templates/workq_main.jinja2')
def my_view(request):
    try:
        session = request.session
        if not 'user_name' in session:
            return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
        active_project_id = session.get("project_id")
        projects = request.dbsession.query(Projects).all()
        json_projects = [{"id": project.id, "name": project.name} for project in projects]

        users = (
            request.dbsession.query(Users)
            .join(UsersProjects, Users.id == UsersProjects.user_id)
            .filter(UsersProjects.project_id == active_project_id)
            .all()
        )

        json_users = [
            {"id": user.id, "name": user.name, "tel": user.tel, "email": user.email, "area": user.area}
            for user in users
        ]
        user_name = session.get('user_name')
        user_email = session.get('user_email')
        user_role = session.get('user_role')
        return {
            "projects": json_projects,
            "active_project_id": active_project_id,
            "users": json_users,
            'user_name': user_name,
            'user_email': user_email,
            'user_role': user_role,
            'current_route': request.path
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