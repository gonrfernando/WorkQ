import allure
import pytest

@allure.title("Load task view")
@allure.suite("System Views")
@allure.sub_suite("Tasks")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Verifies that the task view loads correctly for an authenticated user.")
def test_task_view_load(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    res = testapp.get('/task_view')
    assert res.status_int == 200
    assert 'Task Title' in res.text


@allure.title("Load main project manager view")
@allure.suite("System Views")
@allure.sub_suite("Project Management")
@allure.severity(allure.severity_level.NORMAL)
def test_pm_view_load(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    res = testapp.get('/pm_main')
    assert res.status_int == 200
    assert 'Create Project' in res.text


@allure.title("Load actions view")
@allure.suite("System Views")
@allure.sub_suite("Actions")
@allure.severity(allure.severity_level.NORMAL)
def test_actions_view_load(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    res = testapp.get('/action_view')
    assert res.status_int == 200
    assert 'Actions history' in res.text


@allure.title("Load statistics view")
@allure.suite("System Views")
@allure.sub_suite("Statistics")
@allure.severity(allure.severity_level.NORMAL)
def test_stats_view_load(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    res = testapp.get('/stats_view')
    assert res.status_int == 200
    assert 'Gráfico de estadísticas' in res.text


@allure.title("Load review view")
@allure.suite("System Views")
@allure.sub_suite("Review")
@allure.severity(allure.severity_level.NORMAL)
def test_revision_view_load(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': 'admin@example.com',
        'password': 'admin123'
    })
    res = testapp.get('/revision_view')
    assert res.status_int == 200
    assert 'Revision Content' in res.text


@allure.title("All views require authentication")
@allure.suite("Security")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("path", [
    "/task_view",
    "/pm_main",
    "/stats_view",
    "/action_view",
    "/revision_view",
])
def test_views_require_authentication(testapp, db_session, test_user, path):
    res = testapp.get(path, status=302)
    assert res.location.startswith("http://localhost/sign-in")


@allure.title("Task view loads user's projects")
@allure.suite("System Views")
@allure.sub_suite("Tasks")
@allure.severity(allure.severity_level.NORMAL)
def test_task_view_project_load(testapp, db_session, test_user, test_projects):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.get('/task_view')
    assert res.status_int == 200
    for project in test_projects:
        assert project.name in res.text


@allure.title("Statistics view loads user's projects")
@allure.suite("System Views")
@allure.sub_suite("Statistics")
@allure.severity(allure.severity_level.NORMAL)
def test_stats_view_project_load(testapp, db_session, test_user, test_projects):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.get('/stats_view')
    assert res.status_int == 200
    for project in test_projects:
        assert project.name in res.text


@allure.title("Project manager view shows user's projects")
@allure.suite("System Views")
@allure.sub_suite("Project Management")
@allure.severity(allure.severity_level.NORMAL)
def test_pm_view_project(testapp, db_session, test_user, test_projects):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.get('/pm_main')
    assert res.status_int == 200
    for project in test_projects:
        assert project.name in res.text


@allure.title("Actions view loads user's projects")
@allure.suite("System Views")
@allure.sub_suite("Actions")
@allure.severity(allure.severity_level.NORMAL)
def test_actions_view_project(testapp, db_session, test_user, test_projects):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.get('/action_view')
    assert res.status_int == 200
    for project in test_projects:
        assert project.name in res.text


@allure.title("Review view loads user's projects")
@allure.suite("System Views")
@allure.sub_suite("Review")
@allure.severity(allure.severity_level.NORMAL)
def test_revision_view_project(testapp, db_session, test_user, test_projects):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.get('/revision_view')
    assert res.status_int == 200
    for project in test_projects:
        assert project.name in res.text


@allure.title("Task view shows projects assigned to basic user")
@allure.suite("System Views")
@allure.sub_suite("Tasks")
@allure.severity(allure.severity_level.NORMAL)
def test_task_view_project_user_basic(testapp, db_session, test_user_basic, test_projects, assign_user_to_project):
    testapp.post('/sign-in', {
        'email': test_user_basic.email,
        'password': 'user123'
    })
    res = testapp.get('/task_view')
    assert res.status_int == 200
    assert 'DEBUG: Number of projects: 2' in res.text
    assert 'Project Two' in res.text
    assert 'Project Three' in res.text


@allure.title("Task view shows error message if applicable")
@allure.suite("System Views")
@allure.sub_suite("Tasks")
@allure.severity(allure.severity_level.MINOR)
def test_task_view_error_message_displayed(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.get('/task_view?error=Something+went+wrong')
    assert 'Something went wrong' in res.text

@pytest.mark.parametrize("path", [
    "/pm_main",
    "/action_view",
    "/revision_view",
])
def test_views_roles_management(testapp, db_session, test_user_basic, path):
    testapp.post('/sign-in', {
        'email':test_user_basic.email,
        'password':'user123'
    })
    res = testapp.get(path, status=302)
    assert res.location.startswith("http://localhost/task_view")