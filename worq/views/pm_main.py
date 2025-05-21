from pyramid.view import view_config
from pyramid.response import Response
from worq.models.models import Projects
from pyramid.httpexceptions import HTTPFound
import datetime
from sqlalchemy.exc import SQLAlchemyError
from pyramid.httpexceptions import HTTPFound
from worq.models.models import UsersProjects

@view_config(route_name='pm_main', request_method='POST', renderer='json')
def create_project(request):
    session = request.session
    if 'user_name' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    dbsession = request.dbsession
    active_project_id = session.get("project_id")
    user_id = session.get('user_id')

    
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
