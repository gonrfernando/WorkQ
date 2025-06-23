import pytest
import bcrypt
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from webtest import TestApp
from worq import main  # Este es el factory de tu app Pyramid
from worq.models.models import *

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
    role = Roles(id=1, name='admin')
    db_session.add(role)
    db_session.commit()

    hashed_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = Users(
        id=1,
        name='Admin',
        email='admin@example.com',
        passw=hashed_pw,
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_user_basic(db_session):
    role = Roles(id=2, name='user')
    db_session.add(role)
    db_session.commit()

    hashed_pw = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = Users(
        id=2,
        name='User',
        email='user@example.com',
        passw=hashed_pw,
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()
    return user

# ---------- FIXTURE DE PROYECTO DE PRUEBA ----------
@pytest.fixture
def test_projects(db_session, test_user, test_user_basic):
    state = States(id=1, state='GDL')
    db_session.add(state)
    db_session.commit()
    project1 = Projects(id=1, name="Project One", state_id=state.id, startdate='2025-06-06', enddate='2025-06-06', creationdate='2025-06-06', user_id=1)
    project2 = Projects(id=2, name="Project Two", state_id=state.id, startdate='2025-07-01', enddate='2025-08-01', creationdate='2025-07-01', user_id=2)
    project3 = Projects(id=3, name="Project Three", state_id=state.id, startdate='2025-07-01', enddate='2025-08-01', creationdate='2025-07-01', user_id=2)
    projects = [project1, project2, project3]
    db_session.add_all(projects)
    db_session.flush()
    return projects



@pytest.fixture
def assign_user_to_project(db_session, test_user_basic, test_projects):
    link1 = UsersProjects(user_id=test_user_basic.id, project_id=test_projects[1].id, role_id=2)
    link2 = UsersProjects(user_id=test_user_basic.id, project_id=test_projects[2].id, role_id=2)
    links = [link1, link2]
    db_session.add_all(links)
    db_session.flush()
    return links

@pytest.fixture
def test_priorities(db_session):
    from worq.models.models import TaskPriorities
    p1 = TaskPriorities(id=1, priority="High")
    p2 = TaskPriorities(id=2, priority="Medium")
    db_session.add_all([p1, p2])
    db_session.commit()
    return [p1, p2]

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