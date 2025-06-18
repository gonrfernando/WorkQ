from datetime import datetime, date, timedelta
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError
from worq.models.models import Projects, Tasks, UsersProjects, TaskPriorities, UsersTasks
from sqlalchemy.orm import joinedload

@view_config(route_name='calendar', renderer='worq:templates/calendar.jinja2')
def my_view(request):
    try:
        session = request.session
        if 'user_name' not in session:
            return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

        # Datos de sesión
        active_project_id = session.get("project_id")
        user_name = session.get('user_name')
        user_email = session.get('user_email')
        user_role = session.get('user_role')
        user_id = session.get('user_id')

        # Fecha actual y navegación por mes
        today = date.today()
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        first_day = date(year, month, 1)
        next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

        if user_role == "user" :
            return HTTPFound(location=request.route_url('task_view', _query={'error': 'Sorry, it looks like you don’t have permission to view this content.'}))

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

        # Mapeo de prioridades
        all_priorities = request.dbsession.query(TaskPriorities).all()
        priority_map = {
            p.id: p.priority for p in request.dbsession.query(TaskPriorities).all()
        }

        # Obtener tareas del mes actual
        query = (
        request.dbsession.query(Tasks)
        .options(
            joinedload(Tasks.priority),
            joinedload(Tasks.task_requirements),
            joinedload(Tasks.users)
        )
        .filter(
            Tasks.project_id == active_project_id,
            Tasks.finished_date >= first_day,
            Tasks.finished_date < next_month
        )
    )

    # Si es un user normal, le limitas sólo a sus tareas
        if user_role == "user":
            query = (
                query
                .join(UsersTasks)
                .filter(UsersTasks.user_id == user_id)
            )

        # Ordenas como necesites y ejecutas
        tasks = query.order_by(Tasks.priority_id.desc()).all()


        # Agrupar tareas por día
        tasks_by_day = {}
        for task in tasks:
            if task.finished_date:
                day = task.finished_date.day
                tasks_by_day.setdefault(day, []).append({
                    "id":            task.id,
                    "title":         task.title,
                    "description":   task.description or "",
                    "finished_date":      task.finished_date.isoformat(),
                    "priority_id":   task.priority_id,                      # entero
                    "priority_name": priority_map.get(task.priority_id, "None"), # texto, p.ej. "Low" / "Medium" / "High"
                    "project_id":    task.project_id
                })

        return {
            "projects": json_projects,
            "active_project_id": active_project_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "year": year,
            "month": month,
            "tasks_by_day": tasks_by_day,
            "date": date,
            "timedelta": timedelta
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPInternalServerError("An unexpected error occurred.")
