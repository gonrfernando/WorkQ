from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest
from worq.models.models import Users

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
            return {'message' : error }
        if request.method == 'POST':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            
            print(f"Received data: email={email}, password={password}")

            if '@' and '.' not in email:
                print("Error3")
                return {'message': 'Invalid email address'}

            dbsession = request.dbsession
            
            user = dbsession.query(Users).filter(Users.email==email).first()

            if email == '' or password == '':
                return {'message': 'Email and password are required.'}
            
            if user and user.passw == password:
                session = request.session
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                session['user_role'] = user.role.name
                return HTTPFound(location=request.route_url('home'))
            else:
                return {'message': 'Invalid email or password.'}

        return {}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPInternalServerError("An unexpected error occurred.")