from worq.models.models import Users
import random
import string
import bcrypt
from worq.scripts.emailsender import send_email_async

def reset_user_password(request, email):
    """Genera una nueva contraseña temporal para el usuario y la envía por correo."""
    user = request.dbsession.query(Users).filter(Users.email == email).first()
    if not user:
        return False, 'User not found'

    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
    user.passw = hashed_password.decode('utf-8')
    request.dbsession.flush()

    email_sent = send_email_async(request, email, temp_password)
    if not email_sent:
        return False, 'Failed to send email'

    return True, 'Email sent'
