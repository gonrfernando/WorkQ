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
    print(f"🧪 Connecting to DB: {TEST_DB_URL}")
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

@pytest.fixture
def test_user_pm(db_session):
    role = Roles(id=3, name='project_manager')
    db_session.add(role)
    db_session.commit()

    hashed_pw = bcrypt.hashpw('pm123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = Users(
        id=3,
        name='Project Manager',
        email='pm@example.com',
        passw=hashed_pw,
        role_id=role.id
    )
    db_session.add(user)
    db_session.commit()
    return user
# ---------- FIXTURE DE ROLES, PAÍSES Y ÁREAS ----------
@pytest.fixture
def test_roles(db_session):
    roles = [
        Roles(id=5, name='admin'),
        Roles(id=6, name='user'),
        Roles(id=7, name='project_manager')
    ]
    db_session.add_all(roles)
    db_session.commit()
    return roles
@pytest.fixture
def test_countries(db_session):
    countries = [
        Countries(id=1, name='Mexico'),
        Countries(id=2, name='USA'),
        Countries(id=3, name='Canada')
    ]
    db_session.add_all(countries)
    db_session.commit()
    return countries
@pytest.fixture
def test_areas(db_session):
    areas = [
        Areas(id=1, area='Area 1'),
        Areas(id=2, area='Area 2'),
        Areas(id=3, area='Area 3')
    ]
    db_session.add_all(areas)
    db_session.commit()
    return areas

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
def test_projects_pm(db_session, test_user_pm):
    state = States(id=1, state='GDL')
    db_session.add(state)
    db_session.commit()
    
    project1 = Projects(id=1, name="Project PM One", state_id=state.id, startdate='2025-06-06', enddate='2025-06-06', creationdate='2025-06-06', user_id=test_user_pm.id)
    project2 = Projects(id=2, name="Project PM Two", state_id=state.id, startdate='2025-07-01', enddate='2025-08-01', creationdate='2025-07-01', user_id=test_user_pm.id)
    
    projects = [project1, project2]
    db_session.add_all(projects)
    db_session.flush()
    return projects

@pytest.fixture
def assign_user_to_project_pm(db_session, test_user_pm, test_projects_pm):
    link1 = UsersProjects(user_id=test_user_pm.id, project_id=test_projects_pm[0].id, role_id=3)
    link2 = UsersProjects(user_id=test_user_pm.id, project_id=test_projects_pm[1].id, role_id=3)
    links = [link1, link2]
    db_session.add_all(links)
    db_session.flush()
    return links

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
    p1 = TaskPriorities(id=1, priority="High")
    p2 = TaskPriorities(id=2, priority="Medium")
    db_session.add_all([p1, p2])
    db_session.commit()
    return [p1, p2]

@pytest.fixture
def test_state(db_session):
    deleteds = States(id=2, state='Deleted')
    db_session.add(deleteds)
    db_session.commit()
    return deleteds
# ---------- FIXTURE Test Task ----------
@pytest.fixture
def test_status(db_session):
    status1 = Status(id=1, status_name='Pending', description='Task is pending and not started yet')
    status2 = Status(id=2, status_name='In Progress', description='Task is currently being worked on')
    status3 = Status(id=4, status_name='Completed', description='Task has been completed successfully')
    db_session.add_all([status1, status2, status3])
    db_session.commit()
    return [status1, status2, status3]
@pytest.fixture
def test_tasks(db_session, test_user, test_projects, test_priorities, test_status):
    task1 = Tasks(
        id=100,
        title="Task One",
        description="Description for Task One",
        priority_id=1,
        finished_date='2025-07-01',
        creation_date='2025-06-24',
        project_id=test_projects[0].id,
        status_id=test_status[0].id,  # Asignar estado pendiente
    )
    task2 = Tasks(
        id=200,
        title="Task Two",
        description="Description for Task Two",
        priority_id=2,
        finished_date='2025-07-01',
        creation_date='2025-06-24',
        project_id=test_projects[1].id,
        status_id=test_status[1].id,  # Asignar estado en progreso
    )
    db_session.add_all([task1, task2])
    db_session.commit()
    return [task1, task2]

@pytest.fixture
def test_tasks_pm(db_session, test_user_pm, test_projects_pm, test_priorities, test_status):
    task1 = Tasks(
        id=300,
        title="PM Task One",
        description="Description for PM Task One",
        priority_id=1,
        finished_date='2025-07-01',
        creation_date='2025-06-24',
        project_id=test_projects_pm[0].id,
        status_id=test_status[0].id,  # Asignar estado pendiente
    )
    task2 = Tasks(
        id=400,
        title="PM Task Two",
        description="Description for PM Task Two",
        priority_id=2,
        finished_date='2025-07-01',
        creation_date='2025-06-24',
        project_id=test_projects_pm[1].id,
        status_id=test_status[1].id,  # Asignar estado en progreso
    )
    db_session.add_all([task1, task2])
    db_session.commit()
    return [task1, task2]
# ---------- FIXTURE DE ARCHIVOS ----------
@pytest.fixture
def test_files(db_session):
    file1 = Files(
        id=1,
        filename='test_file_1.txt',
        filepath='path/to/test_file_1.txt'
    )
    file2 = Files(
        id=2,
        filename='test_file_2.txt',
        filepath='path/to/test_file_2.txt'
    )
    db_session.add_all([file1, file2])
    db_session.commit()
    return [file1, file2]
@pytest.fixture
def test_task_files(db_session, test_files, test_tasks):
    task_file1 = TaskFiles(
        id=1,
        task_id=test_tasks[0].id,  # Asumiendo que tienes una tarea con ID 100
        file_id=test_files[0].id
    )
    task_file2 = TaskFiles(
        id=2,
        task_id=test_tasks[1].id,  # Asumiendo que tienes una tarea con ID 200
        file_id=test_files[1].id
    )
    db_session.add_all([task_file1, task_file2])
    db_session.commit()
    return [task_file1, task_file2]
# ---------- FIXTURE DE REVISIÓN DE SOLICITUDES ----------
@pytest.fixture
def test_requests(db_session, test_user, test_projects, test_status):
    request1 = Requests(
        id=1,
        action_type="Description for Request One",
        project_id=test_projects[0].id,
        user_id=test_user.id,
        status_id=test_status[0].id,  
        reason="Test reason for request one",
        request_date=datetime.datetime.now()
    )
    request2 = Requests(
        id=2,
        action_type="Test Request Two",
        project_id=test_projects[0].id,
        user_id=test_user.id,
        status_id=test_status[0].id, 
        reason="Test reason for request two",
        request_date=datetime.datetime.now()
    )
    db_session.add_all([request1, request2])
    db_session.commit()
    return [request1, request2]
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