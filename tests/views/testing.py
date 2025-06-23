import pytest
from worq.models.models import *
import json

def test_delete_project_status_success(testapp, db_session, test_user, test_projects):
    # Simular login
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })

    # Enviar POST JSON a la ruta
    res = testapp.post('/delete_project_status',
        params=json.dumps({'project_id': 50}),
        content_type='application/json'
    )

    # Verificar respuesta
    assert res.status_code == 200
    json_data = res.json
    assert json_data['success'] is False
    assert json_data['error'] == 'Project not found'
