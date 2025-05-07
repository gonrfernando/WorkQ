from pyramid.view import view_config
@view_config(route_name='info_user', renderer='templates/user_info.jinja2')
def sign_in_view(request):
    return {}