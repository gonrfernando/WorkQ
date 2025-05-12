from pyramid.view import view_config
from pyramid.response import Response
from worq.models.models import Projects
import datetime
from sqlalchemy.exc import SQLAlchemyError
from pyramid.httpexceptions import HTTPFound
from worq.models.models import UsersProjects

@view_config(route_name='pm_main', renderer='templates/pm_main.jinja2', request_method='GET')
def pm_main_view(request):
    session = request.session
    if not 'user_name' in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
    active_project_id = session.get("project_id")
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    user_id = session.get('user_id')
    
    project_ids = request.dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
    json_projects = [{"id": project.project_id, "name": project.project.name} for project in project_ids]
    
    return {
        "projects": json_projects,
        "active_project_id": active_project_id,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role
    }

@view_config(route_name='pm_main', request_method='POST', renderer='json')
def create_project(request):
    try:
        if not request.body:
            return Response("Empty request body", content_type='text/plain', status=400)

        try:
            data = request.json_body
        except ValueError:
            return Response("Invalid JSON", content_type='text/plain', status=400)

        name = data.get('name')
        startdate = data.get('startdate')
        enddate = data.get('enddate')


        if not name or not startdate:
            return Response("Missing required fields", content_type='text/plain', status=400)

        new_project = Projects(
            name=name,
            startdate=datetime.datetime.strptime(startdate, '%Y-%m-%d').date(),
            enddate=datetime.datetime.strptime(enddate, '%Y-%m-%d').date() if enddate else None,
            creationdate=datetime.date.today(),
            state_id=1  # Valor predeterminado
        )

        request.dbsession.add(new_project)
        request.dbsession.flush()

        return {"success": True, "message": "Project created successfully"}
    except SQLAlchemyError as e:
        return Response(str(e), content_type='text/plain', status=500)
