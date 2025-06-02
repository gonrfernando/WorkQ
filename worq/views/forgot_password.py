from worq.scripts.forgot_pass import reset_user_password
from pyramid.view import view_config

@view_config(route_name='forgot_password', renderer='templates/sign_in.jinja2')
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('emailfp', '').strip()
        print(email)
        if not email or '@' not in email:
            return {
                'message': 'Please enter a valid email.',
                'status': 'error'
            }

        success, msg = reset_user_password(request, email)
        status = 'success' if success else 'error'
        return {
            'message': msg,
            'status': status,
            'email_value': email
        }

    return {}
