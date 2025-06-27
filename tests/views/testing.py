from worq.models.models import *
import allure
import pytest
import datetime
import json
import allure
import allure

import allure


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


@allure.title("Update user allows password change")
@allure.suite("Edit User View")
@allure.sub_suite("POST")
@allure.severity(allure.severity_level.NORMAL)
def test_update_user_with_password(testapp, db_session, test_user, test_countries, test_areas, test_roles):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    new_password = "newpass123"

    res = testapp.post_json('/update_user', {
        "user_id": test_user.id,
        "passw": new_password,
        "name": test_user.name,
        "email": test_user.email,
        "tel": test_user.tel,
        "country_id": test_user.country_id,
        "area_id": test_user.area_id,
        "role_id": test_user.role_id
    }, status=200)

    json_data = res.json
    assert json_data['success'] is True

    # El password queda como texto plano (si no usas hash aquí)
    updated = db_session.query(Users).get(test_user.id)
    assert updated.passw == new_password


