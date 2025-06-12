import pytest
import bcrypt
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from webtest import TestApp
from worq import main  # Este es el factory de tu app Pyramid
from worq.models.models import Base, Users, Roles

# URL de la base de datos de prueba (debes haberla creado previamente)
TEST_DB_URL = "postgresql://postgres:CETI360@3.137.178.132/test_db"

# ---------- FIXTURES DE BASE DE DATOS ----------

@pytest.fixture(scope='session')
def engine():
    return create_engine(TEST_DB_URL)


@pytest.fixture(scope='session')
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, tables):
    """Crea una sesión transaccional aislada para cada prueba"""
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))
    yield session
    transaction.rollback()
    session.remove()
    connection.close()


# ---------- FIXTURE DE USUARIO DE PRUEBA ----------

@pytest.fixture
def test_user(db_session):
    """Inserta un usuario admin@example.com con password admin123 y un rol"""
    role = Roles(id=1, name='Admin')
    db_session.add(role)
    db_session.commit()

    hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = Users(
        name='Admin',
        email='admin@example.com',
        passw=hashed_pw,
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()
    return user


# ---------- FIXTURE DE LA APP WEB (WebTest) ----------

@pytest.fixture
def testapp(db_session):
    settings = {
        'sqlalchemy.url': TEST_DB_URL,
        'pyramid.includes': [],
    }

    app = main({}, **settings)

    # Envolvemos la app con WebTest
    test_app = TestApp(app)

    # Inyectamos la sesión en el entorno para que sea tomada por request.dbsession
    def add_dbsession(environ, start_response):
        environ['app.dbsession'] = db_session
        return app(environ, start_response)

    test_app.app = add_dbsession
    return test_app