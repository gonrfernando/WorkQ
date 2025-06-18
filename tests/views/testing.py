def test_task_view_error_message_displayed(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })

    res = testapp.get('/task_view?error=Something+went+wrong')
    assert 'Something went wrong' in res.text
