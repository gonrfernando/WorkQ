from pyramid.view import view_config

@view_config(route_name='startpage', renderer='templates/startpage.jinja2')
def index_view(request):
    return {
        'title': "WorkQ - A new form of working together",
        'navbar_links': [
            {'label': 'Help', 'href': '#'},
            {'label': 'About', 'href': '#'},
            {'label': 'Documentation', 'href': '#'}
        ],
        'what_is_workq': "WorkQ is a platform designed to facilitate collaboration and improve productivity in teams...",
        'goal_description': "The goal that we want to reach is a new form of working together..."
    }
