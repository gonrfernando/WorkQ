import pytest
def test_task_creation_get_renders(testapp, test_user, db_session, test_priorities):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.get('/add_task')
    assert res.status_int == 200
    assert "add task" in res.text.lower()  
def test_edit_project_update(testapp, db_session, test_user, test_projects, capsys):
    # Simular inicio de sesión
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })

    # Cargar la página de edición del proyecto
    res = testapp.post('/edit_project', {
    'project_id': test_projects[0].id,
    'form_type':'edit_project',
    'name':'Project 1',
    'startdate':'2025-05-01',
    'enddate':'2026-05-01'
    }, status=200)

    assert res.status_int == 200
    captured = capsys.readouterr()
    assert f"[SUCCESS] Project updated successfully: ID {test_projects[0].id}" in captured.out

def test_edit_project_not_p_id(testapp , capsys, test_user, db_session, test_projects, test_priorities):
    # Simular inicio de sesión
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })

    # Cargar la página de edición del proyecto
    res = testapp.post('/edit_project', {
    'project_id': ''
    })

    assert res.status_int == 302
    captured = capsys.readouterr()
    assert "[ERROR] No project_id provided." in captured.out

def test_edit_project_not_found_p(testapp , capsys, test_user):
    # Simular inicio de sesión
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })

    # Cargar la página de edición del proyecto
    res = testapp.post('/edit_project', {
    'project_id': 1
    })

    assert res.status_int == 302
    captured = capsys.readouterr()
    assert f"[ERROR] Project not found. ID: 1" in captured.out

def test_edit_project_not_found_p(testapp, db_session, test_user, test_projects):
    # Simular inicio de sesión
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })

    # Cargar la página de edición del proyecto
    res = testapp.post('/edit_project', {
    'project_id': 1,
    'form_type':''
    })

    assert res.status_code == 200
    assert res.content_type == 'application/json'
    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == 'Invalid form type'

@pytest.mark.parametrize("name, startdate, enddate", [
    ("", "2024-01-01", "2024-12-31"),   # Falta name
    ("Test Project", "", "2024-12-31"), # Falta startdate
    ("Test Project", "2024-01-01", ""), # Falta enddate
])
def test_edit_project_missing_fields(testapp, test_user, test_projects, name, startdate, enddate):
    # Simular inicio de sesión
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })

    # Enviar POST sin uno de los campos requeridos
    res = testapp.post('/edit_project', {
        'project_id': test_projects[0].id,
        'form_type': 'edit_project',
        'name': name,
        'startdate': startdate,
        'enddate': enddate
    })

    # Validaciones
    assert res.status_code == 200
    assert res.content_type == 'application/json'
    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == 'Name, Start Date and End Date are required'
