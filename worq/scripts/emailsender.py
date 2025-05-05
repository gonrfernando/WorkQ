import smtplib
from email.message import EmailMessage

def send_email(request, to_email, content):
    msg = EmailMessage()
    msg["Subject"] = "Tu contraseña temporal"
    msg["From"] = "Ce360worq@gmail.com"
    msg["To"] = to_email
    msg.set_content(f"""
    Hola 👋

    Esta es tu contraseña temporal para ingresar al sistema:

    {content}

    ¡No la compartas con nadie!
    """)

    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login("9abc83595b2a88", "75f90074523f91")  # asegúrate de poner tu password real aquí
            server.send_message(msg)
        print(f"Correo enviado a {to_email}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")
