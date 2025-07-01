import io
import re
import pytest
import allure
from worq.scripts.sanitize import (
    allowed_file,
    sanitize_filename,
    validate_file_size,
    sanitize_file,
    MAX_FILE_SIZE,
    ALLOWED_EXTENSIONS,
)

@allure.title("Validate allowed extensions")
@allure.suite("File Validation")
@allure.sub_suite("allowed_file")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize("filename, expected", [
    ("image.png", True),
    ("report.pdf", True),
    ("script.exe", False),
    ("notes.txt", True),
    ("malware.sh", False),
    ("", False),
])
def test_allowed_file(filename, expected):
    assert allowed_file(filename) == expected


@allure.title("Sanitize filename with invalid characters")
@allure.suite("File Sanitization")
@allure.sub_suite("sanitize_filename")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("Should replace special characters with underscores and keep the extension.")
def test_sanitize_filename_removes_invalid_chars():
    dirty_name = "my file@!name$#%.pdf"
    clean_name = sanitize_filename(dirty_name)
    assert re.match(r'^[a-zA-Z0-9_.-]+$', clean_name)
    assert clean_name.endswith(".pdf")


@allure.title("Validate file within size limit")
@allure.suite("File Validation")
@allure.sub_suite("validate_file_size")
@allure.severity(allure.severity_level.CRITICAL)
def test_validate_file_size_valid():
    fake_file = io.BytesIO(b"12345" * 100)  # ~0.5 KB
    validate_file_size(fake_file)


@allure.title("Reject file exceeding size limit")
@allure.suite("File Validation")
@allure.sub_suite("validate_file_size")
@allure.severity(allure.severity_level.CRITICAL)
def test_validate_file_size_exceeds():
    fake_file = io.BytesIO(b"a" * (MAX_FILE_SIZE + 1))
    with pytest.raises(ValueError, match="File size exceeds"):
        validate_file_size(fake_file)


@allure.title("Sanitize valid file")
@allure.suite("File Sanitization")
@allure.sub_suite("sanitize_file")
@allure.severity(allure.severity_level.NORMAL)
def test_sanitize_file_valid():
    fake_file = io.BytesIO(b"Hello")
    filename = "doc.txt"
    result = sanitize_file(fake_file, filename)
    assert result.endswith("doc.txt")


@allure.title("Reject file with not allowed extension")
@allure.suite("File Sanitization")
@allure.sub_suite("sanitize_file")
@allure.severity(allure.severity_level.CRITICAL)
def test_sanitize_file_invalid_extension():
    fake_file = io.BytesIO(b"Hello")
    filename = "malware.exe"
    with pytest.raises(ValueError, match="File type not allowed"):
        sanitize_file(fake_file, filename)


@allure.title("Reject valid file but too large")
@allure.suite("File Sanitization")
@allure.sub_suite("sanitize_file")
@allure.severity(allure.severity_level.CRITICAL)
def test_sanitize_file_invalid_size():
    fake_file = io.BytesIO(b"a" * (MAX_FILE_SIZE + 1))
    filename = "image.jpg"
    with pytest.raises(ValueError, match="File size exceeds"):
        sanitize_file(fake_file, filename)
