from pyramid.view import view_config

@view_config(route_name='add_user', renderer='templates/add_user.jinja2')
def add_user_test_view(request):
    departments = [
        {'id': 1, 'name': 'Engineering'},
        {'id': 2, 'name': 'HR'},
        {'id': 3, 'name': 'Marketing'}
    ]
    roles = [
        {'id': 1, 'name': 'Admin'},
        {'id': 2, 'name': 'User'},
        {'id': 3, 'name': 'Guest'}
    ]
    return {
        'departments': departments,
        'roles': roles
    }