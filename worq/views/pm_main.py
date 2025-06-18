import datetime
import transaction
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from sqlalchemy.exc import SQLAlchemyError
from worq.models.models import Projects, UsersProjects
import json

@view_config(route_name='pm_main', renderer='worq:templates/pm_main.jinja2', request_method=('GET', 'POST'))
def project_creation_view(request):
    session = request.session
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    if 'user_name' not in session:
        return HTTPFound(
            location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'})
        )

    dbsession = request.dbsession

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
    active_project_id = session.get("project_id") or (user_projects[0].id if user_projects else None)
    session["project_id"] = active_project_id
    active_project_id = int(active_project_id) if active_project_id else None
    active_project = next((p for p in json_projects if p["id"] == active_project_id), None)

    # POST: crear proyecto
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = request.json_body
            else:
                data = request.POST

            name = data.get('name')
            startdate = data.get('startdate')
            enddate = data.get('enddate')
            today = datetime.date.today()

# Validación: startdate no en el pasado
            start_date_obj = datetime.datetime.strptime(startdate, '%Y-%m-%d').date()
            if start_date_obj < today:
                return Response("La fecha de inicio no puede ser en el pasado.", status=400)

            # Validación: enddate no antes de startdate (si se proporciona)
            if enddate:
                end_date_obj = datetime.datetime.strptime(enddate, '%Y-%m-%d').date()
                if end_date_obj < start_date_obj:
                    return Response("La fecha de fin no puede ser anterior a la de inicio.", status=400)
            if not name or not startdate:
                return Response(
                    "Missing required fields: 'name' and 'startdate' are mandatory",
                    status=400,
                    content_type='text/plain'
                )

            new_proj = Projects(
                name=name,
                startdate=datetime.datetime.strptime(startdate, '%Y-%m-%d').date(),
                enddate=(datetime.datetime.strptime(enddate, '%Y-%m-%d').date()
                        if enddate else None),
                creationdate=datetime.date.today(),
                state_id=1,
                user_id=user_id
            )
            dbsession.add(new_proj)
            dbsession.flush()
            print("Nuevo proyecto ID:", new_proj.id)

            transaction.commit()

            session["project_id"] = new_proj.id

            # Si es AJAX, responde JSON
            is_ajax = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or 'application/json' in request.headers.get('Accept', '')
        )

            if is_ajax:
                return Response(
                    json.dumps({"success": True}),
                    content_type='application/json; charset=utf-8'
                )
            return HTTPFound(location=request.route_url('pm_main'))
    
        except SQLAlchemyError as e:
            if is_ajax:
                return Response(
                    json.dumps({"success": False, "error": str(e)}),
                    content_type='application/json; charset=utf-8',
                    status=500
                )
            return Response(str(e), status=500, content_type='text/plain')
        except Exception as e:
            if is_ajax:
                return Response(
                    json.dumps({"success": False, "error": "Invalid request: " + str(e)}),
                    content_type='application/json; charset=utf-8',
                    status=400
                )
            return Response("Invalid request: " + str(e), status=400, content_type='text/plain')

    # Si es GET (o si caíste acá tras un POST fallido), renderiza normalmente
    return {
        "projects":          json_projects,
        "active_project":    active_project,
        "active_project_id": active_project_id,
        "user_name":         session.get('user_name'),
        "user_email":        session.get('user_email'),
        "user_role":         session.get('user_role'),
        "now": datetime.datetime.utcnow().strftime('%Y-%m-%d')
    }
