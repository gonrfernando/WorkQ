from pyramid.view import view_config
from pyramid.response import Response
import json

@view_config(route_name='save_active_tab', request_method='POST', renderer='json')
def save_active_tab(request):
    try:
        data = json.loads(request.body)
        active_tab = data.get('active_tab')
        if active_tab:
            request.session['active_tab'] = active_tab
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}