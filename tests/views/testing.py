import pytest
from worq.models.models import *
import json
def delete_projects_success(testapp , capsys, test_user, db_session, test_projects, test_priorities):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    res = testapp.post('/delete_projects_status',params=json.dumps({
        'project_id': 1
    }),
    content_type='application/json'
    )


    captured = capsys.readouterr()
    assert f"[SUCCESS] Project marked as deleted: ID {test_projects[0].id} (state_id={test_projects[0].state_id})" in captured.out