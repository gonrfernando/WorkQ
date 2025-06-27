import allure
from worq.views.sign_up import sign_up_view
from worq.models.models import Users


@allure.title("Load login page")
@allure.suite("Authentication")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that the login page loads correctly with status code 200.")
def test_login_page_loads(testapp):
    res = testapp.get('/sign-in', status=200)
    assert 'Sign-in' in res.text


@allure.title("Successful login with valid credentials")
@allure.suite("Authentication")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("Tests that login works with correct username and password.")
def test_login_success(testapp, db_session, test_user):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'admin@example.com'
    form['password'] = 'admin123'
    response = form.submit()
    assert response.status_int == 302


@allure.title("Login fails with incorrect password")
@allure.suite("Authentication")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that the system rejects incorrect passwords.")
def test_login_failure(testapp, db_session, test_user):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'admin@example.com'
    form['password'] = 'Contraseña erronea'
    response = form.submit()
    assert response.status_int == 200  
    assert 'Invalid email or password.' in response.text


@allure.title("Login fails with empty fields")
@allure.suite("Authentication")
@allure.severity(allure.severity_level.MINOR)
@allure.description("Checks that the system detects empty fields in login.")
def test_login_empty_fields(testapp):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = ''
    form['password'] = ''
    response = form.submit()
    assert response.status_int == 200
    assert 'Email and password are required.' in response.text


@allure.title("Login fails with invalid email format")
@allure.suite("Authentication")
@allure.severity(allure.severity_level.MINOR)
@allure.description("Checks that the email format is validated correctly.")
def test_login_invalid_email_format(testapp):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'email'
    form['password'] = 'passw'
    response = form.submit()
    assert response.status_int == 200
    assert 'Invalid email address' in response.text


@allure.title("Login fails with unregistered user")
@allure.suite("Authentication")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that a non-existent user cannot log in.")
def test_login_notfounduser(testapp, db_session, test_user):
    res = testapp.get('/sign-in')
    form = res.forms[0]
    form['email'] = 'notfound@user.com'
    form['password'] = 'nd'
    response = form.submit()
    assert response.status_int == 200
    assert 'Invalid email or password.' in response.text


@allure.title("Redirect if already authenticated on login")
@allure.suite("Authentication")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that if already authenticated, a redirect message is shown.")
def test_login_already_auth(testapp, db_session, test_user):
    testapp.post('/sign-in', {'email': 'admin@example.com', 'password': 'admin123'})
    res = testapp.get('/sign-in')
    assert res.status_int == 200
    assert 'You are already logged in. Redirecting to the home page in 5 seconds...' in res.text


@allure.title("Load sign-up page")
@allure.suite("Registration")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that the registration page loads correctly.")
def test_sign_up_page_loads(testapp):
    res = testapp.get('/sign-up', status=200)
    assert 'Sign-up' in res.text


@allure.title("Successful registration with valid email")
@allure.suite("Registration")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("Checks that a new user can register successfully.")
def test_sign_up_form_success(testapp, db_session, test_user):
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = 'admin@example.com'
    response = form.submit()
    assert response.status_int == 200


@allure.title("Registration fails with empty field")
@allure.suite("Registration")
@allure.severity(allure.severity_level.MINOR)
@allure.description("Checks that the email field is required for registration.")
def test_sign_up_empty_field(testapp, db_session, test_user):
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = ''
    response = form.submit()
    assert response.status_int == 200
    assert 'Please complete the email' in response.text


@allure.title("Registration fails with invalid email")
@allure.suite("Registration")
@allure.severity(allure.severity_level.MINOR)
@allure.description("Checks that the system rejects emails with incorrect format.")
def test_sign_up_email_format(testapp, db_session, test_user):
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = 'CorreoInvalido'
    response = form.submit()
    assert response.status_int == 200
    assert 'Invalid email' in response.text


@allure.title("Registration fails if email already exists")
@allure.suite("Registration")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that an existing email cannot be registered again.")
def test_sign_up_user_already_existing(testapp, db_session, test_user):
    existing_email = 'user@exists.com'
    existing_user = Users(id=4, email=existing_email, passw='dummyhash', role_id=1)
    db_session.add(existing_user)
    db_session.flush()
    res = testapp.get('/sign-up')
    form = res.forms[0]
    form['email'] = existing_email
    response = form.submit()
    assert response.status_int == 200
    assert 'Email already exists' in response.text


@allure.title("Redirect on registration if already logged in")
@allure.suite("Registration")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that the user is redirected if already logged in during registration.")
def test_sign_up_redirect_if_logged_in(testapp, db_session, test_user):
    testapp.post('/sign-in', {'email': 'admin@example.com', 'password': 'admin123'})
    res = testapp.get('/sign-up')
    assert res.status_int == 200
    assert 'Already logged in. Redirecting...' in res.text


@allure.title("Resend email without session email")
@allure.suite("Registration")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Checks that email cannot be resent if there is no email in the session.")
def test_resend_email_without_session_email(testapp):
    res = testapp.get('/sign-up?resend=1')
    assert res.status_int == 200
    assert 'No email found in session.' in res.text


@allure.title("Error resending email due to system failure")
@allure.suite("Registration")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Simulates an error when resending the verification email.")
def test_resend_error_path(monkeypatch, testapp, db_session):
    monkeypatch.setattr('worq.views.sign_up.send_email_async', lambda *a, **kw: False)
    res = testapp.get('/sign-up?resend=1')
    assert res.status_int == 200
    assert 'Failed to resend email.' in res.text
