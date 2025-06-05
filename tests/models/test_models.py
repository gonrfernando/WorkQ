# tests/test_users.py
import pytest
from sqlalchemy.exc import IntegrityError
from worq.models.models import Users, Roles, Areas, Countries

def test_create_user(db_session):
    role = Roles(name="Admin")
    db_session.add(role)
    db_session.commit()

    user = Users(name="Juan Pérez", email="juan@test.com", passw="hashedpass", role_id=role.id)
    db_session.add(user)
    db_session.commit()

    fetched_user = db_session.query(Users).filter_by(email="juan@test.com").first()
    assert fetched_user is not None
    assert fetched_user.name == "Juan Pérez"
    assert fetched_user.role.name == "Admin"

def test_usuario_email_required(db_session):
    role = Roles(name="Admin")
    db_session.add(role)
    db_session.commit()
    usuario = Users(name="Carlos", passw="secret", role_id=role.id)
    db_session.add(usuario)
    
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_usuario_passw_required(db_session):
    role = Roles(name="Admin")
    db_session.add(role)
    db_session.commit()
    usuario = Users(name="Carlos", email="car@los.com", role_id=role.id)
    db_session.add(usuario)
    
    with pytest.raises(IntegrityError):
        db_session.commit()

def test_usuario_roleid_required(db_session):
    usuario = Users(name="Carlos",email="Car@lo.s", passw="secret")
    db_session.add(usuario)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_usuario_roles(db_session):
    rol = Roles(name="admin")
    db_session.add(rol)
    db_session.commit()
    usuario = Users(name="Ana", email="ana@test.com", passw="123", role_id=rol.id)
    
    db_session.add(usuario)
    db_session.commit()
    
    assert usuario.role.name == "admin"

def test_usuario_areas(db_session):
    area = Areas(area="IT")
    db_session.add(area)
    db_session.commit()
    rol = Roles(name="admin")
    db_session.add(rol)
    db_session.commit()

    usuario = Users(name="Ana", email="ana@test.com", passw="123", role_id=rol.id, area_id=area.id)
    
    db_session.add(usuario)
    db_session.commit()
    
    assert usuario.area.area == "IT"

def test_usuario_countries(db_session):
    country = Countries(name="Mexico")
    db_session.add(country)
    db_session.commit()
    rol = Roles(name="admin")
    db_session.add(rol)
    db_session.commit()

    usuario = Users(name="Ana", email="ana@test.com", passw="123", role_id=rol.id, country_id=country.id)
    
    db_session.add(usuario)
    db_session.commit()
    
    assert usuario.country.name == "Mexico"