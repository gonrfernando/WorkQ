from datetime import datetime, date, timedelta
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError
from worq.models.models import Projects, Tasks, UsersProjects, TaskPriorities


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

        # Obtener proyectos del usuario
        user_projects = request.dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
        json_projects = [{"id": up.project_id, "name": up.project.name} for up in user_projects]

        # Mapeo de prioridades
        priority_map = {
            p.id: p.priority for p in request.dbsession.query(TaskPriorities).all()
        }

        # Obtener tareas del mes actual
        tasks = request.dbsession.query(Tasks).filter(
            Tasks.project_id == active_project_id,
            Tasks.finished_date >= first_day,
            Tasks.finished_date < next_month
        ).all()

        # Agrupar tareas por día
        tasks_by_day = {}
        for task in tasks:
            if task.finished_date:
                day = task.finished_date.day
                tasks_by_day.setdefault(day, []).append({
                    "title": task.title,
                    "description": task.description,
                    "finished_date": task.finished_date.isoformat(),
                    "priority": priority_map.get(task.priority_id, "None")
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
