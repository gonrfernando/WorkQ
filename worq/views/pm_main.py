import datetime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from sqlalchemy.exc import SQLAlchemyError

from worq.models.models import Projects

@view_config(route_name='pm_main',renderer='worq:templates/pm_main.jinja2',request_method=('GET', 'POST'))
def project_creation_view(request):
    session = request.session
    if 'user_name' not in session:
        return HTTPFound(
            location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'})
        )

    dbsession = request.dbsession

    # 2) Obtener lista de proyectos existentes y proyecto activo en sesión
    all_projects = dbsession.query(Projects).all()
    json_projects = [{"id": p.id, "name": p.name} for p in all_projects]

    active_project_id = session.get("project_id")
    if not active_project_id and all_projects:
        # si no hay activo, tomo el primero
        active_project_id = all_projects[0].id
        session["project_id"] = active_project_id
    active_project_id = int(active_project_id) if active_project_id is not None else None
    active_project = next((p for p in json_projects if p["id"] == active_project_id), None)

    # 3) Manejo de POST: crear un proyecto nuevo
    if request.method == 'POST':
        name      = request.POST.get('name')
        startdate = request.POST.get('startdate')
        enddate   = request.POST.get('enddate')

        # Validaciones básicas
        if not name or not startdate:
            return Response(
                "Missing required fields: 'name' and 'startdate' are mandatory",
                status=400,
                content_type='text/plain'
            )

        try:
            new_proj = Projects(
                name=name,
                startdate=datetime.datetime.strptime(startdate, '%Y-%m-%d').date(),
                enddate=datetime.datetime.strptime(enddate, '%Y-%m-%d').date() if enddate else None,
                creationdate=datetime.date.today(),
                state_id=1  # estado por defecto
            )
            dbsession.add(new_proj)
            dbsession.flush()  # para obtener ID

            # actualizar lista y proyecto activo en la respuesta
            json_projects.append({"id": new_proj.id, "name": new_proj.name})
            # opcional: hacer que el nuevo proyecto sea el activo
            session["project_id"] = new_proj.id
            active_project = {"id": new_proj.id, "name": new_proj.name}

        except SQLAlchemyError as e:
            return Response(str(e), status=500, content_type='text/plain')

    # 4) Renderizar plantilla con datos
    return {
        "projects":          json_projects,
        "active_project":    active_project,
        "active_project_id": active_project_id,
        "user_name":         session.get('user_name'),
        "user_email":        session.get('user_email'),
        "user_role":         session.get('user_role'),
    }
