def test_forgot_password_success(monkeypatch, testapp, db_session):
    # Setup: agregar usuario a la DB
    from worq.models.models import Users, Roles
    import bcrypt

    role = Roles(id=2, name='User')
    db_session.add(role)
    db_session.flush()

    email = 'testuser@example.com'
    hashed_pwd = bcrypt.hashpw(b'123456', bcrypt.gensalt()).decode('utf-8')
    user = Users(email=email, passw=hashed_pwd, role_id=role.id)
    db_session.add(user)
    db_session.commit()

    # Mock: reset_user_password para evitar enviar correos
    monkeypatch.setattr(
        'worq.scripts.forgot_pass.reset_user_password',
        lambda req, email_arg: (True, 'Recovery email sent.')
    )

    # Realizar POST al endpoint
    res = testapp.post('/forgot-password', params={'emailfp': email})

    # Verificar que el mensaje de éxito esté presente
    assert 'Recovery email sent.' in res.text
    assert 'success' in res.text



