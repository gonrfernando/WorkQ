import pytest
from worq.models.models import *
def test_create_project_success(testapp, db_session, test_user):
    testapp.post('/sign-in', {
        'email': test_user.email,
        'password': 'admin123'
    })
    data = {
        "name": "New Project",
        "startdate": "2025-07-01",
        "enddate": "2025-07-30"
    }
    res = testapp.post('/pm_main', data)
    assert res.status_int == 200
    assert db_session.query(Projects).filter_by(name="New Project").one_or_none() is not None
