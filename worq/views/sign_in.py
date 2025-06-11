from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError, HTTPFound
from worq.models.models import Users
import bcrypt

@view_config(route_name='sign_in', renderer='templates/sign_in.jinja2')
def sign_in_view(request):
    try:
        session = request.session
        if 'user_name' in session:
            return {
                'message': 'You are already logged in. Redirecting to the home page in 5 seconds...',
                'redirect': True  # Indicador para activar el redireccionamiento en la plantilla
            }
        error = request.params.get('error')
        if error:
            return {'message': error}
        
        if request.method == 'POST':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            
            print(f"Received data: email={email}, password={password}")

            if email == '' or password == '':
                return {'message': 'Email and password are required.'}
            
            if '@' not in email or '.' not in email:
                print("Error: Invalid email format")
                return {'message': 'Invalid email address'}

            dbsession = request.dbsession
            user = dbsession.query(Users).filter(Users.email == email).first()

            
            if user:
                # Verificar la contraseña usando bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), user.passw.encode('utf-8')):
                    # Contraseña válida, iniciar sesión
                    session['user_name'] = user.name
                    session['user_email'] = user.email
                    session['user_role'] = user.role.name
                    session['user_id'] = user.id
                    return HTTPFound(location=request.route_url('task_view'))
                else:
                    # Contraseña inválida
                    return {'message': 'Invalid email or password.'}
            else:
                # Usuario no encontrado
                return {'message': 'Invalid email or password.'}

        return {}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPInternalServerError("An unexpected error occurred.")