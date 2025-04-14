import smtplib
from email.message import EmailMessage
from pyramid.settings import asbool

def send_email(request, to_email, temp_password):
    settings = request.registry.settings

    msg = EmailMessage()
    msg['Subject'] = 'Tu contraseña provisional'
    msg['From'] = settings['mail.username']
    msg['To'] = to_email
    msg.set_content(f'Tu contraseña provisional para ingresar es: {temp_password}')

    with smtplib.SMTP(settings['mail.host'], int(settings['mail.port'])) as server:
        if asbool(settings.get('mail.tls', 'false')):
            server.starttls()
        server.login(settings['mail.username'], settings['mail.password'])
        server.send_message(msg)
        