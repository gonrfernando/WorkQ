from pyramid.view import view_config
@view_config(route_name='sign_in', renderer='templates/sign_in.jinja2')
def sign_in_view(request):
    return {}