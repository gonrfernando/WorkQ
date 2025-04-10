from pyramid.view import view_config
@view_config(route_name='sign_up', renderer='templates/sign_up.jinja2')
def sign_up_view(request):
    return {}
