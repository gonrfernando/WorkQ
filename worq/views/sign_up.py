from pyramid.view import view_config
from worq.models.modelos import Users
import random
import string
from worq.scripts.emailsender import send_email
@view_config(route_name='sign_up', renderer='templates/sign_up.jinja2')
def sign_up_view(request):
    try:
        email = request.POST.get('email', '').strip()
        user = request.dbsession.query(Users).filter(Users.email==email).first()
        if user:
            print(f"User with email {email} already exists.")
            return {'message': 'Email already exists'}
        lenght = 8
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=lenght))
        dbsession = request.dbsession
        new_user = Users(email=email, password=temp_password)
        dbsession.add(new_user)
        dbsession.flush()

        send_email(request, email, temp_password)
        return {'message': 'Temporary password sent to your email'}
    except Exception as e:
        # Log the error message
        print(f"Error: {e}")
        return {'message': 'An unexpected error occurred. Please try again.'}