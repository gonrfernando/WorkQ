from datetime import datetime, date, timedelta
from worq.models.models import Projects, Tasks, UsersProjects
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPInternalServerError


@view_config(route_name='calendar', renderer='worq:templates/calendar.jinja2')
def my_view(request):
    try:
        session = request.session
        if not 'user_name' in session:
            return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))
        active_project_id = session.get("project_id")
        user_name = session.get('user_name')
        user_email = session.get('user_email')
        user_role = session.get('user_role')
        user_id = session.get('user_id')

        today = date.today()
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        first_day = date(year, month, 1)
        if month == 12:
            next_month = date(year+1, 1, 1)
        else:
            next_month = date(year, month+1, 1)

        project_ids = request.dbsession.query(UsersProjects).filter_by(user_id=user_id).all()
        json_projects = [{"id": project.project_id, "name": project.project.name} for project in project_ids]

        tasks = request.dbsession.query(Tasks).filter(
            Tasks.project_id == active_project_id,
            Tasks.finished_date >= first_day,
            Tasks.finished_date < next_month
        ).all()

        tasks_by_day = {}
        for task in tasks:
            if task.finished_date:
                day = task.finished_date.day
                tasks_by_day.setdefault(day, []).append({
                    "title": task.title,
                    "decription": task.description,
                    "finished_date": task.finished_date.isoformat(),
                    "priority": task.priority
                })
            

        return {
            "projects": json_projects,
            "active_project_id": active_project_id,
            'user_name': user_name,
            'user_email': user_email,
            'user_role': user_role,
            'year': year,
            'month': month,
            'tasks_by_day': tasks_by_day,
            'date': date,
            'timedelta': timedelta
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPInternalServerError("An unexpected error occurred.")
