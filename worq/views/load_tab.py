from pyramid.view import view_config
@view_config(route_name='get_active_tab', request_method='GET', renderer='json')
def get_active_tab(request):
    active_tab = request.session.get('active_tab', None)
    return {'active_tab': active_tab}