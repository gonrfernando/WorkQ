import pytest
import json
import allure
import datetime
from worq.models.models import *

from unittest.mock import patch


@allure.title("Files by task - Success")
@allure.suite("Task Files View")
@allure.sub_suite("GET")
@allure.severity(allure.severity_level.CRITICAL)
def test_files_by_task_success(testapp, db_session, test_user, test_tasks, test_files, test_task_files):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get(f'/files_by_task?task_id={test_tasks[0].id}', status=200)
    
    json_data = res.json
    assert json_data['status'] == 'ok'
    assert isinstance(json_data['files'], list)
    assert all('id' in f and 'filename' in f and 'url' in f for f in json_data['files'])

@allure.title("Files by task - Missing task_id")
@allure.suite("Task Files View")
@allure.sub_suite("GET")
@allure.severity(allure.severity_level.NORMAL)
def test_files_by_task_missing_task_id(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.get('/files_by_task', status=200)

    json_data = res.json
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Missing task_id'


import worq.scripts.s3_utils as s3_utils
from unittest.mock import patch

@allure.title("Files by task - URL generation failure handled")
@allure.suite("Task Files View")
@allure.sub_suite("GET")
@allure.severity(allure.severity_level.MINOR)
def test_files_by_task_presigned_url_failure(testapp, db_session, test_user, test_tasks, test_files, test_task_files):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})

    with patch.object(s3_utils, 'generate_presigned_url', side_effect=Exception("Mocked S3 error")):
        res = testapp.get(f'/files_by_task?task_id={test_tasks[0].id}', status=200)

    json_data = res.json
    assert json_data['status'] == 'ok'
    assert all(f['url'] is None for f in json_data['files'])


@allure.title("Delete file - Missing file_id")
def test_delete_file_missing_id(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/delete_file', {}, status=200)
    assert res.json['status'] == 'error'
    assert 'missing' in res.json['message'].lower()

@allure.title("Delete file - File not found")
def test_delete_file_not_found(testapp, test_user):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})
    res = testapp.post('/delete_file', {'file_id': '9999'}, status=200)
    assert res.json['status'] == 'error'
    assert 'not found' in res.json['message'].lower()

@allure.title("Delete file - Success")
def test_delete_file_success(testapp, db_session, test_user, test_files, test_task_files):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})

    file_id = test_files[0].id

    with patch('worq.views.delete_files.delete_file_from_s3', return_value=True):
        res = testapp.post('/delete_file', {'file_id': str(file_id)}, status=200)
        assert res.json['status'] == 'ok'
        assert 'deleted' in res.json['message'].lower()


@allure.title("Delete file - S3 failure")
def test_delete_file_s3_failure(testapp, test_user, test_files):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})

    file_id = test_files[0].id

    with patch('worq.views.delete_files.delete_file_from_s3', return_value=False):
        res = testapp.post('/delete_file', {'file_id': str(file_id)}, status=200)
        assert res.json['status'] == 'error'
        assert 'could not delete' in res.json['message'].lower()

@allure.title("Delete file - S3 throws exception")
def test_delete_file_s3_exception(testapp, test_user, test_files):
    testapp.post('/sign-in', {'email': test_user.email, 'password': 'admin123'})

    file_id = test_files[0].id

    with patch('worq.views.delete_files.delete_file_from_s3', side_effect=Exception("S3 error")):
        res = testapp.post('/delete_file', {'file_id': str(file_id)}, status=200)
        assert res.json['status'] == 'error'
        assert 'exception' in res.json['message'].lower()