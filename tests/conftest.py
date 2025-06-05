# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from worq.models.models import Base

TEST_DB_URL = "postgresql://test_user:test_Workq_360@localhost/test_db_worq"

@pytest.fixture(scope='session')
def engine():
    return create_engine(TEST_DB_URL)  # o PostgreSQL temporal

@pytest.fixture(scope='session')
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, tables):
    """Retorna una sesión con la base de datos en memoria"""
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))
    yield session
    transaction.rollback()
    connection.close()
    session.remove()