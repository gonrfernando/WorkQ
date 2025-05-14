from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from worq.models.models import Users
import json



def json_response(data, status=200):
    return Response(
        body=json.dumps(data).encode('utf-8'),
        status=status,
        content_type='application/json; charset=utf-8'
    )


@view_config(route_name='info_user', renderer='templates/user_info.jinja2', request_method='GET')
def info_user_get(request):
    session = request.session

    if 'user_email' not in session:
        return HTTPFound(location=request.route_url('sign_in', _query={'error': 'Sign in to continue.'}))

    user_email = session.get('user_email')
    user = request.dbsession.query(Users).filter_by(email=user_email).first()

    if not user:
        return {
            'user_name': session.get('user_name'),
            'user_email': user_email,
            'user_role': session.get('user_role'),
            'user_tel': None,
            'error': 'User not found.'
        }

    return {
        'user_name': user.name,
        'user_email': user.email,
        'user_role': session.get('user_role'),
        'user_tel': user.tel
    }

@view_config(route_name='info_user', request_method='POST')
def info_user_post(request):
    session = request.session

    if 'user_email' not in session:
        return json_response({'success': False, 'error': 'User not signed in'}, status=401)

    try:
        user_email = session.get('user_email')
        user = request.dbsession.query(Users).filter_by(email=user_email).first()

        if not user:
            return json_response({'success': False, 'error': 'User not found'}, status=404)

        name = request.POST.get('name')
        number = request.POST.get('number')

        user.name = name
        user.tel = number
        request.dbsession.flush()

        session['user_name'] = name

        return json_response({'success': True})

    except Exception as e:
        print(f"Error: {e}")
        return json_response({'success': False, 'error': 'An unexpected error occurred'}, status=500)

@view_config(route_name='info_user', request_method='PUT')
def info_user_put(request):
    session = request.session

    if 'user_email' not in session:
        return json_response({'success': False, 'error': 'User not signed in'}, status=401)

    try:
        user_email = session.get('user_email')
        user = request.dbsession.query(Users).filter_by(email=user_email).first()

        if not user:
            return json_response({'success': False, 'error': 'User not found'}, status=404)

        old_password = request.POST.get('pass')
        new_password = request.POST.get('n_pass')
        con_new_password = request.POST.get('cn_pass')

        if user.passw != old_password:
            return json_response({'success': False, 'error': 'Incorrect old password'}, status=403)

        if new_password != con_new_password:
            return json_response({'success': False, 'error': 'New passwords do not match'}, status=400)

        user.passw= new_password
        request.dbsession.flush()

        return json_response({'success': True, 'message': 'Password updated successfully'})

    except Exception as e:
        print(f"Error: {e}")
        return json_response({'success': False, 'error': 'An unexpected error occurred'}, status=500)
