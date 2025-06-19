from unittest.mock import patch, MagicMock
from worq.scripts.emailsender import send_email_async

def test_send_email_async():
    mock_request = MagicMock()
    mock_request.registry.settings = {
        'smtp.host': 'smtp.example.com',
        'smtp.port': 587,
        'smtp.user': 'test_user@example.com',
        'smtp.pass': 'test_password'
    }

    to_email = "test@example.com"
    temp_password = "temporary123"

    with patch('worq.scripts.emailsender.smtplib.SMTP') as mock_smtp:
        mock_server = mock_smtp.return_value.__enter__.return_value  # para manejar el contexto (with)
        mock_server.starttls.return_value = None
        mock_server.login.return_value = None
        mock_server.sendmail.return_value = None

        result = send_email_async(mock_request, to_email, temp_password)

        assert result is True
        mock_smtp.assert_called_once_with('smtp.example.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test_user@example.com', 'test_password')
        mock_server.sendmail.assert_called_once()
