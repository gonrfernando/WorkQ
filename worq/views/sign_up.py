from pyramid.view import view_config
from worq.models.models import Users
from pyramid.httpexceptions import HTTPFound
import random
import string
import bcrypt
from worq.scripts.emailsender import send_email_async  # Asegúrate de importar la correcta

from datetime import datetime, timedelta

@view_config(route_name='sign_up', renderer='templates/sign_up.jinja2')
def sign_up_view(request):
    try:
        session = request.session

        # Si se solicita reenvío
        if 'resend' in request.params:
            last_sent_str = session.get('email_last_sent')
            now = datetime.utcnow()
            if last_sent_str:
                last_sent = datetime.fromisoformat(last_sent_str)
                if (now - last_sent).total_seconds() < 45:
                    remaining = 45 - int((now - last_sent).total_seconds())
                    return {
                        'message': f'Please wait {remaining} seconds before resending.',
                        'status': 'error',
                        'email_sent': True,
                        'email_value': session.get('email')
                    }

            email = session.get('email')
            if not email:
                return {'message': 'No email found in session.', 'status': 'error'}

            # Nueva contraseña temporal
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            email_sent = send_email_async(request, email, temp_password)

            if not email_sent:
                return {'message': 'Failed to resend email.', 'status': 'error'}

            session['email_last_sent'] = now

            return {
                'message': 'Email resent successfully.',
                'status': 'success',
                'email_sent': True,
                'email_value': email
            }

        if 'user_name' in session:
            return {'message': 'Already logged in. Redirecting...', 'redirect': True, 'status': 'error'}

        if request.method == 'POST':
            email = request.POST.get('email', '').strip()
            if not email or '@' not in email or '.' not in email:
                return {'message': 'Invalid email', 'status': 'error'}

            user = request.dbsession.query(Users).filter(Users.email == email).first()
            if user:
                return {'message': 'Email already exists', 'status': 'error'}

            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            email_sent = send_email_async(request, email, temp_password)

            if not email_sent:
                return {'message': 'Failed to send email.', 'status': 'error'}

            hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
            new_user = Users(email=email, passw=hashed_password.decode('utf-8'), role_id=4)

            request.dbsession.add(new_user)
            request.dbsession.flush()

            # Guardar en sesión
            session['email'] = email
            session['email_last_sent'] = datetime.utcnow().isoformat()


            return {
                'message': 'Temporary password sent to your email.',
                'status': 'success',
                'email_sent': True,
                'email_value': email
            }

        return {}

    except Exception as e:
        print(f"Error: {e}")
        return {'message': 'Unexpected error occurred.', 'status': 'error'}

