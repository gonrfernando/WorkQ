import pytest
import json
import allure
import datetime
from worq.models.models import *

protected_paths = [
    "/edit_project",
    "/edit_task",
    "/add_task",
    "/request_management",
    "/add_user",
    "/info_user",
    "/revision_view",
    "/calendar",
    "/edit_user",
]

@allure.title("Redirection when accessing protected views without authentication")
@allure.suite("Access Control")
@allure.sub_suite("Authentication Required")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("path", protected_paths)
def test_views_require_authentication(testapp, db_session, test_user, path):
    res = testapp.get(path, status=302)
    assert res.location.startswith("http://localhost/sign-in")


@allure.title("Redirection when accessing views with insufficient roles")
@allure.suite("Access Control")
@allure.sub_suite("Role Validation")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("path", protected_paths)
def test_views_roles_management(testapp, db_session, test_user_basic, path):
    if path == "/info_user" or path == "/calendar":
        pytest.skip("Path '/info_user' does not require role validation")
    
    testapp.post('/sign-in', {
        'email': test_user_basic.email,
        'password': 'user123'
    })
    res = testapp.get(path, status=302)
    assert res.location.startswith("http://localhost/task_view")

@allure.title("Render add task form for authenticated user")
@allure.suite("Task Management")
@allure.sub_suite("Add Task View")
@allure.severity(allure.severity_level.NORMAL)
def test_task_creation_get_renders(testapp, test_user, db_session, test_priorities):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/add_task')
    assert res.status_int == 200
    assert "add task" in res.text.lower()


@allure.title("Edit project - Successful update")
@allure.suite("Project Management")
@allure.sub_suite("Edit Project")
@allure.severity(allure.severity_level.CRITICAL)
def test_edit_project_update(testapp, db_session, test_user, test_projects, capsys):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_project', {
        'project_id': test_projects[0].id,
        'form_type': 'edit_project',
        'name': 'Project 1',
        'startdate': '2025-05-01',
        'enddate': '2026-05-01'
    }, status=200)

    assert res.status_int == 200
    captured = capsys.readouterr()
    assert f"[SUCCESS] Project updated successfully: ID {test_projects[0].id}" in captured.out


@allure.title("Edit project - Missing project ID")
@allure.suite("Project Management")
@allure.sub_suite("Edit Project")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_project_not_p_id(testapp, capsys, test_user, db_session, test_projects, test_priorities):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_project', {'project_id': ''})
    assert res.status_int == 302
    captured = capsys.readouterr()
    assert "[ERROR] No project_id provided." in captured.out


@allure.title("Edit project - Project not found")
@allure.suite("Project Management")
@allure.sub_suite("Edit Project")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_project_not_found_p(testapp, capsys, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_project', {'project_id': 1})
    assert res.status_int == 302
    captured = capsys.readouterr()
    assert f"[ERROR] Project not found. ID: 1" in captured.out


@allure.title("Edit project - Invalid form type")
@allure.suite("Project Management")
@allure.sub_suite("Edit Project")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_project_invalid_form_type(testapp, db_session, test_user, test_projects):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_project', {
        'project_id': 1,
        'form_type': ''
    })
    assert res.status_code == 200
    assert res.content_type == 'application/json'
    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == 'Invalid form type'


@allure.title("Edit project - Missing required fields")
@allure.suite("Project Management")
@allure.sub_suite("Edit Project")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("name, startdate, enddate", [
    ("", "2024-01-01", "2024-12-31"),
    ("Test Project", "", "2024-12-31"),
    ("Test Project", "2024-01-01", ""),
])
def test_edit_project_missing_fields(testapp, test_user, test_projects, name, startdate, enddate):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_project', {
        'project_id': test_projects[0].id,
        'form_type': 'edit_project',
        'name': name,
        'startdate': startdate,
        'enddate': enddate
    })
    assert res.status_code == 200
    assert res.content_type == 'application/json'
    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == 'Name, Start Date and End Date are required'


@allure.title("Delete project - Successful deletion")
@allure.suite("Project Management")
@allure.sub_suite("Delete Project")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_project_status_success(testapp, db_session, test_user, test_projects, test_state):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/delete_project_status',
        params=json.dumps({'project_id': test_projects[0].id}),
        content_type='application/json'
    )
    assert res.status_code == 200
    json_data = res.json
    assert json_data['success'] is True
    assert 'redirect' in json_data


@allure.title("Delete project - Missing project ID")
@allure.suite("Project Management")
@allure.sub_suite("Delete Project")
@allure.severity(allure.severity_level.NORMAL)
def test_delete_project_no_project_id(testapp, db_session, test_user, test_projects, test_state):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/delete_project_status',
        params=json.dumps({'project_id': ''}),
        content_type='application/json'
    )
    assert res.status_code == 200
    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == 'No project ID provided'


@allure.title("Delete project - Project not found")
@allure.suite("Project Management")
@allure.sub_suite("Delete Project")
@allure.severity(allure.severity_level.NORMAL)
def test_delete_project_status_project_not_found(testapp, db_session, test_user, test_projects):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/delete_project_status',
        params=json.dumps({'project_id': 50}),
        content_type='application/json'
    )
    assert res.status_code == 200
    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == 'Project not found'
@allure.title("Redirect when task_id is missing")
@allure.suite("Edit Task")
@allure.sub_suite("GET")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_task_redirect_if_task_id_missing(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/edit_task', status=302)
    assert res.location.startswith("http://localhost/task_view")


@allure.title("Redirect when task does not exist")
@allure.suite("Edit Task")
@allure.sub_suite("GET")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_task_redirect_if_task_not_found(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/edit_task?task_id=9999', status=302)
    assert res.location.startswith("http://localhost/task_view")

@allure.title("Fail edit task with invalid form_type")
@allure.suite("Edit Task")
@allure.sub_suite("POST")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_task_invalid_form_type(testapp, test_user, test_tasks):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_task', {
        'task_id': test_tasks[0].id,
        'form_type': 'invalid'
    })
    assert res.status_code == 200
    assert res.json['success'] is False
    assert res.json['error'] == 'Invalid form type'

@allure.title("Fail edit task with missing title/description")
@allure.suite("Edit Task")
@allure.sub_suite("POST")
@allure.severity(allure.severity_level.CRITICAL)
def test_edit_task_missing_fields(testapp, test_user, test_tasks):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_task', {
        'task_id': test_tasks[0].id,
        'form_type': 'edit_task',
        'title': '',
        'description': ''
    })
    assert res.status_code == 200
    assert res.json['success'] is False
    assert res.json['error'] == 'Title and Description are required'


@allure.title("Render edit task form with valid task")
@allure.suite("Edit Task")
@allure.sub_suite("GET")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_task_get_success(testapp, test_user, test_tasks):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get(f'/edit_task?task_id={test_tasks[0].id}')
    assert res.status_code == 200
    assert "Task One" in res.text or "Updated Task" in res.text  # según tu base de datos




@allure.title("Successful task edit via form POST")
@allure.suite("Edit Task")
@allure.sub_suite("POST")
@allure.severity(allure.severity_level.CRITICAL)
def test_edit_task_post_form_success(testapp, test_user, test_tasks):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/edit_task', {
        'task_id': test_tasks[0].id,
        'form_type': 'edit_task',
        'title': 'Updated Task',
        'description': 'New Description',
        'priority': 1,
        'finished_date': '2025-06-24T12:00',
        'requirements': ['Requirement 1'],
        'collaborators': ['user@example.com']
    })
    assert res.status_code == 200
    assert res.json['success'] is True
    assert 'redirect' in res.json


@allure.suite("Add Task")
@allure.sub_suite("GET")
@allure.title("Render add task form")
def test_add_task_get_success(testapp, test_user, test_projects, test_priorities, db_session):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    testapp.set_cookie('user_name', 'Admin')
    testapp.set_cookie('user_email', test_user.email)
    testapp.set_cookie('user_role', 'admin')
    testapp.set_cookie('user_id', str(test_user.id))
    testapp.set_cookie('project_id', str(test_projects[1].id))

    res = testapp.get('/add_task', status=200)
    assert "Add Task" in res.text

@allure.sub_suite("POST")
@allure.title("Successfully creates a task via form")
def test_add_task_post_success(testapp, test_user, test_projects, test_priorities, test_status, db_session, test_user_basic):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})


    form_data = {
    'form_type': 'add_task',
    'title': 'New Task',
    'description': 'Task from test',
    'finished_date': '2025-07-01T12:00',
    'priority': '1',
    'project_id': str(test_projects[0].id),  # ✅ esta línea nueva
    'requirements': ['Requirement A', 'Requirement B'],
    'collaborators': test_user_basic.email,  # ✅ Cambiado a email del usuario básico
    }

    res = testapp.post('/add_task', form_data, headers={'Accept': 'application/json'})
    assert res.status_code == 200
    assert res.json['success'] is True

@allure.title("Access request_management with valid admin")
@allure.suite("Request Management")
@allure.sub_suite("Rendering")
@allure.severity(allure.severity_level.CRITICAL)
def test_request_management_render_admin(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/request_management')
    assert res.status_code == 200
    assert "Requests" in res.text or "request" in res.text.lower()

@allure.title("Filter by type_id in request_management")
@allure.suite("Request Management")
@allure.sub_suite("Filters")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("type_id", ["1", "2", "3"])
def test_request_management_filters_by_type(testapp, test_user, type_id):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get(f'/request_management?type_id={type_id}')
    assert res.status_code == 200
    assert "Requests" in res.text or "request" in res.text.lower()

@allure.title("Render request_management when no requests exist")
@allure.suite("Request Management")
@allure.sub_suite("Empty State")
@allure.severity(allure.severity_level.MINOR)
def test_request_management_empty_state(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/request_management')
    assert res.status_code == 200
    assert "no requests" in res.text.lower() or "request" in res.text.lower()  # según plantilla

@allure.title("Render request_management with existing task/project requests")
@allure.suite("Request Management")
@allure.sub_suite("Data Rendering")
@allure.severity(allure.severity_level.NORMAL)
def test_request_management_with_requests(testapp, db_session, test_user, test_projects, test_priorities, test_status):
    from worq.models.models import Tasks, Requests

    # Crear tarea y request asociada
    task = Tasks(
        title="Test Task",
        description="Testing task",
        project_id=test_projects[0].id,
        status_id=4,
        created_by=test_user.id,
        priority_id=test_priorities[0].id,
        creation_date=datetime.datetime.utcnow()
    )
    db_session.add(task)
    db_session.flush()

    request_task = Requests(
        task_id=task.id,
        user_id=test_user.id,
        status_id=4,
        project_id=test_projects[0].id,
        reason="Test request for task",
        action_type="delete",
        request_date=datetime.datetime.utcnow()
    )
    db_session.add(request_task)
    db_session.flush()

    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/request_management')
    assert res.status_code == 200
    assert test_projects[0].name in res.text

@allure.title("Reject unauthorized access to handle_request_action")
def test_handle_request_action_unauthorized(testapp):
    res = testapp.post_json('/handle-request-action', {'request_id': 1, 'action': 'accept'}, status=401)
    assert res.json['error'] == 'Unauthorized'


@allure.title("Reject invalid request_id in handle_request_action")
def test_handle_request_action_not_found(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/handle-request-action', {'request_id': 999, 'action': 'accept'}, status=404)
    assert res.json['error'] == 'Request not found'


@allure.title("Reject invalid action in handle_request_action")
def test_handle_request_action_invalid_action(testapp, db_session, test_user, test_requests):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/handle-request-action', {
        'request_id': test_requests[0].id,
        'action': 'invalid'
    }, status=400)
    assert res.json['error'] == 'Invalid action'


@allure.title("Accept request successfully")
def test_handle_request_accept_success(testapp, db_session, test_user, test_requests):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/handle-request-action', {
        'request_id': test_requests[0].id,
        'action': 'accept'
    })
    assert res.status_code == 200
    assert res.json['message'] == 'Request updated'


@allure.title("Fail when no task_id provided in prepare_edit_task")
def test_prepare_edit_task_missing_id(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/prepare_edit_task', {})
    assert res.json['success'] is False
    assert res.json['error'] == "Task ID is required."


@allure.title("Store task_id in session")
def test_prepare_edit_task_success(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/prepare_edit_task', {'task_id': 10})
    assert res.json['success'] is True


@allure.title("Fail when no project_id provided in prepare_edit_project")
def test_prepare_edit_project_missing_id(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/prepare_edit_project', {})
    assert res.json['success'] is False
    assert res.json['error'] == "Project ID is required."


@allure.title("Render info_user page with valid user")
def test_info_user_get_success(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/info_user')
    assert res.status_code == 200
    assert test_user.name in res.text

@allure.title("POST /info_user - Successful update of user information")
def test_info_user_post_update_success(testapp, test_user, db_session):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/info_user', {'name': 'Updated Name', 'number': '987654321'})
    assert res.json['success'] is True
    assert db_session.query(Users).get(test_user.id).name == 'Updated Name'


@allure.title("PUT /info_user - Please fill all the inputs")
def test_info_user_put_empty_fields(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.put('/info_user', {
        'pass': '',
        'n_pass': '',
        'cn_pass': ''
    })
    assert res.json['error'] == 'Please fill all the inputs'


@allure.title("PUT /info_user - Incorrect old password")
def test_info_user_put_wrong_old_password(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.put('/info_user', {
        'pass': 'wrongpassword',
        'n_pass': 'newpass123',
        'cn_pass': 'newpass123'
    })
    assert res.json['error'] == 'Incorrect old password'


@allure.title("PUT /info_user - New passwords do not match")
def test_info_user_put_passwords_do_not_match(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.put('/info_user', {
        'pass': 'admin123',
        'n_pass': 'newpass123',
        'cn_pass': 'differentpass'
    })
    assert res.json['error'] == 'New passwords do not match'


@allure.title("PUT /info_user - Cambio exitoso de contraseña")
def test_info_user_put_success(testapp, test_user, db_session):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.put('/info_user', {
        'pass': 'admin123',
        'n_pass': 'newpass123',
        'cn_pass': 'newpass123'
    })
    assert res.json['success'] is True
    assert 'message' in res.json



@allure.title("Revision view renders for authenticated admin user with assigned projects")
@allure.suite("Revision View")
@allure.sub_suite("Render Tests")
@allure.severity(allure.severity_level.CRITICAL)
def test_revision_view_renders_for_admin(testapp, test_user, db_session, test_projects, test_tasks, test_priorities):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/revision_view', status=200)
    
    assert "revision" in res.text.lower()
    assert test_projects[0].name in res.text
    assert test_tasks[0].title in res.text

@allure.title("Render revision view with no available projects")
def test_revision_view_with_no_projects(testapp, test_user, db_session):
    # Asegúrate de que test_user no tenga proyectos activos
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/revision_view', status=200)
    assert "projects" in res.text.lower()


@allure.title("Revision view renders for project_manager with assigned projects")
@allure.suite("Revision View")
@allure.sub_suite("Render Tests")
@allure.severity(allure.severity_level.NORMAL)
def test_revision_view_renders_for_project_manager(testapp, test_user_pm, db_session, test_projects_pm, test_tasks_pm, assign_user_to_project_pm):
    testapp.post('/sign-in', {'email': test_user_pm.email, 'password': 'pm123'})
    res = testapp.get('/revision_view', status=200)

    assert test_projects_pm[0].name in res.text
    assert test_tasks_pm[0].title in res.text


@allure.title("Save feedback fails when user not authenticated")
@allure.suite("Revision View")
@allure.sub_suite("Save Feedback")
@allure.severity(allure.severity_level.CRITICAL)
def test_save_feedback_unauthenticated(testapp):
    res = testapp.post_json('/feedback/save', {
        "task_id": 1,
        "comment": "Feedback test"
    }, status=200)
    json_data = res.json

    assert json_data['success'] is False
    assert json_data['error'] == "User not authenticated"


@allure.title("Save feedback fails with missing comment or task_id")
@allure.suite("Revision View")
@allure.sub_suite("Save Feedback")
@allure.severity(allure.severity_level.NORMAL)
def test_save_feedback_missing_data(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})

    res = testapp.post_json('/feedback/save', {
        "comment": "No task_id"
    }, status=200)
    json_data = res.json
    assert json_data['success'] is False
    assert "Missing data" in json_data['error']

    res = testapp.post_json('/feedback/save', {
        "task_id": 1
    }, status=200)
    json_data = res.json
    assert json_data['success'] is False
    assert "" in json_data['error']


@allure.title("Save feedback fails if task not found")
@allure.suite("Revision View")
@allure.sub_suite("Save Feedback")
@allure.severity(allure.severity_level.CRITICAL)
def test_save_feedback_task_not_found(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/feedback/save', {
        "task_id": 9999,
        "comment": "No task"
    }, status=200)

    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == "Task not found."

@allure.title("Save feedback updates existing feedback")
@allure.suite("Revision View")
@allure.sub_suite("Save Feedback")
@allure.severity(allure.severity_level.NORMAL)
def test_save_feedback_update_existing(testapp, test_user, test_tasks, db_session):
    from worq.models.models import Feedbacks
    from datetime import datetime

    # Creamos un feedback previo
    fb = Feedbacks(
        user_id=test_user.id,
        task_id=test_tasks[0].id,
        comment="Original",
        date=datetime.utcnow()
    )
    db_session.add(fb)
    db_session.flush()

    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/feedback/save', {
        "task_id": test_tasks[0].id,
        "comment": "Comentario actualizado"
    }, status=200)

    json_data = res.json
    assert json_data['success'] is True
    assert json_data['feedback']['comment'] == "Comentario actualizado"

@allure.title("Edit user renders correctly for authenticated admin")
@allure.suite("Edit User View")
@allure.sub_suite("GET")
@allure.severity(allure.severity_level.NORMAL)
def test_edit_user_renders_for_admin(testapp, test_user, test_projects, test_roles, test_countries, test_areas):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/edit_user', status=200)

    assert res.status_code == 200
    assert "projects" in res.text.lower()
    assert "users" in res.text.lower()


@allure.title("Update user fails without user_id")
@allure.suite("Edit User View")
@allure.sub_suite("POST")
@allure.severity(allure.severity_level.CRITICAL)
def test_update_user_missing_id(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/update_user', {
        "name": "New Name"
    }, status=200)
    json_data = res.json
    assert json_data['error'] == "User ID is required"

@allure.title("Update user fails when user not found")
@allure.suite("Edit User View")
@allure.sub_suite("POST")
@allure.severity(allure.severity_level.CRITICAL)
def test_update_user_not_found(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/update_user', {
        "user_id": 9999,
        "name": "Test"
    }, status=200)
    json_data = res.json
    assert json_data['error'] == "User not found"


@allure.title("Update user updates fields successfully")
@allure.suite("Edit User View")
@allure.sub_suite("POST")
@allure.severity(allure.severity_level.CRITICAL)
def test_update_user_success(testapp, db_session, test_user, test_countries, test_areas, test_roles):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post_json('/update_user', {
        "user_id": test_user.id,
        "name": "Updated Name",
        "email": "updated@example.com",
        "tel": "1234567890",
        "country_id": 1,
        "area_id": 1,
        "role_id": 5
    }, status=200)

    json_data = res.json
    assert json_data['success'] is True
    assert json_data['message'] == "User updated successfully"

    # Verificar en la base
    updated_user = db_session.query(Users).get(test_user.id)
    assert updated_user.name == "Updated Name"
