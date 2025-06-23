from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError
from worq.models.models import Projects, Users, UsersProjects

@view_config(route_name='home', renderer='worq:templates/workq_main.jinja2')
def my_view(request):
    try:
        session = request.session

        # Validación de sesión
        if 'user_name' not in session:
            return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

        # Datos del usuario desde la sesión
        user_id = session.get('user_id')
        error = request.params.get('error')
        active_project_id = session.get("project_id")
        user_name = session.get('user_name')
        user_email = session.get('user_email')
        user_role = session.get('user_role')
        user_icon = session.get('user_icon')
        active_project_id = session.get("project_id")

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

        # 👥 Obtener usuarios del proyecto activo (si hay uno definido)
        json_users = []
        if active_project_id:
            users = (
                request.dbsession.query(Users)
                .join(UsersProjects, Users.id == UsersProjects.user_id)
                .filter(UsersProjects.project_id == active_project_id)
                .all()
            )
            json_users = [
                {
                    "id": user.id,
                    "name": user.name,
                    "tel": user.tel,
                    "email": user.email,
                    "area": user.area
                } for user in users
            ]

        return {
            "projects": json_projects,
            "active_project_id": active_project_id,
            "users": json_users,
            'user_name': user_name,
            'user_email': user_email,
            'user_role': user_role,
            'current_route': request.path,
            'message': error if error else None,
            'user_icon': user_icon
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
