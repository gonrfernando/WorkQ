def test_task_view_project(testapp, db_session, test_user_basic, test_projects):
    testapp.post('/sign-in', {
        'email': test_user_basic.email,
        'password': 'user123'
    })

    res = testapp.get('/task_view')
    assert res.status_int == 200
    print(res.text)
    assert 'DEBUG: Number of projects: 2' in res.text

    for project in test_projects:
        assert project.name in res.text