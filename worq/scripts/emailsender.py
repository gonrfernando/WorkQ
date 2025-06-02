import smtplib
from email.mime.text import MIMEText

def send_email_async(request, to_email, temp_password):
    try:
        settings = request.registry.settings

        smtp_server = settings.get('smtp.host')
        smtp_port = int(settings.get('smtp.port', 587))
        smtp_user = settings.get('smtp.user')
        smtp_pass = settings.get('smtp.pass')
        from_email = smtp_user  # usamos el mismo correo como remitente

        subject = "Tu contraseña temporal"
        body = f"Tu contraseña temporal es: {temp_password}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [to_email], msg.as_string())

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
