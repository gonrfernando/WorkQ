from pyramid.view import view_config
from pyramid.response import Response
from worq.models.models import Projects
import datetime
from sqlalchemy.exc import SQLAlchemyError

@view_config(route_name='pm_main', renderer='templates/pm_main.jinja2', request_method='GET')
def pm_main_view(request):
    session = request.session    
    projects = request.dbsession.query(Projects).all()
    json_projects = [{"id": project.id, "name": project.name} for project in projects]
    active_project_id = request.params.get("project_id")
    user_name = session.get('user_name')
    user_email = session.get('user_email')
    user_role = session.get('user_role')
    return {
        "projects": json_projects,
        "active_project_id": active_project_id,
        'user_name': user_name,
        'user_email': user_email,
        'user_role': user_role,
        'active_tab': "pm"
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
