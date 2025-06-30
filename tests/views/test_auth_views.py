from worq.views.sign_up import sign_up_view
from worq.models.models import Users


def test_login_page_loads(testapp):
    res = testapp.get('/sign-in', status=200)
    assert 'Sign-in' in res.text

def test_login_success(testapp, db_session, test_user):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'admin@example.com'
    form['password'] = 'admin123'
    response = form.submit()

    assert response.status_int == 302  # Redirige a /tasks o similar

def test_login_failure(testapp, db_session, test_user):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'admin@example.com'
    form['password'] = 'Contraseña erronea'
    response = form.submit()

    assert response.status_int == 200  
    assert 'Invalid email or password.' in response.text

def test_login_empty_fields(testapp):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = ''
    form['password'] = ''
    response = form.submit()

    assert response.status_int == 200
    assert 'Email and password are required.' in response.text

def test_login_invalid_email_format(testapp):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'email'
    form['password'] = 'passw'
    response = form.submit()

    assert response.status_int == 200
    assert 'Invalid email address' in response.text

def test_login_notfounduser(testapp, db_session, test_user):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'notfound@user.com'
    form['password'] = 'nd'
    response = form.submit()

    assert response.status_int == 200
    assert 'Invalid email or password.' in response.text

def test_login_already_auth(testapp, db_session, test_user):
    res = testapp.post('/sign-in', {
        'email' : 'admin@example.com',
        'password': 'admin123'
    })

    res = testapp.get('/sign-in')

    assert res.status_int == 200
    assert 'You are already logged in. Redirecting to the home page in 5 seconds...' in res.text
    assert 'setTimeout(function()' in res.text
    assert '/home' in res.text or 'window.location.href = "' in res.text

def test_sign_up_page_loads(testapp):
    res = testapp.get('/sign-up', status=200)
    assert 'Sign-up' in res.text

def test_sign_up_form_success(testapp, db_session, test_user):
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = 'admin@example.com'
    response = form.submit()

    assert response.status_int == 200
    
def test_sign_up_empty_field(testapp, db_session, test_user):
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = ''
    response = form.submit()

    assert response.status_int == 200
    assert 'Please complete the email' in response.text

def test_sign_up_email_format(testapp, db_session, test_user):
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = 'CorreoInvalido'
    response = form.submit()

    assert response.status_int == 200
    assert 'Invalid email' in response.text

def test_sign_up_user_already_existing(testapp, db_session, test_user):
    existing_email = 'user@exists.com'
    existing_user = Users(email=existing_email, passw='dummyhash', role_id=1)
    db_session.add(existing_user)
    db_session.flush()

    # Ir al formulario y enviar el correo duplicado
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = existing_email
    response = form.submit()

    assert response.status_int == 200
    assert 'Email already exists' in response.text

def test_sign_up_redirect_if_logged_in(testapp, db_session, test_user):
    # Inicia sesión primero
    testapp.post('/sign-in', {
        'email': 'admin@example.com',
        'password': 'admin123'
    })

    res = testapp.get('/sign-up')

    assert res.status_int == 200
    assert 'Already logged in. Redirecting...' in res.text

def test_resend_email_without_session_email(testapp):
    res = testapp.get('/sign-up?resend=1')

    assert res.status_int == 200
    assert 'No email found in session.' in res.text
    assert '"status": "error"' in res.text or 'error' in res.text.lower()

def test_resend_error_path(monkeypatch, testapp, db_session):

    monkeypatch.setattr('worq.views.sign_up.send_email_async', lambda *a, **kw: False)
    res = testapp.get('/sign-up?resend=1')
    assert res.status_int == 200
    assert 'Failed to resend email.' in res.text
    assert 'error' in res.text


