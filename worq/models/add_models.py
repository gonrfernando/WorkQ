# coding: utf-8
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Area(Base):
    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True, server_default=text("nextval('areas_id_seq'::regclass)"))
    name = Column(String(100), nullable=False)
    status = Column(Boolean, nullable=False)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, server_default=text("nextval('roles_id_seq'::regclass)"))
    name = Column(String(100), nullable=False)
    status = Column(Boolean, nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_id_seq'::regclass)"))
    role_id = Column(ForeignKey('roles.id'), nullable=False)
    area_id = Column(ForeignKey('areas.id'), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(12), nullable=False)

    area = relationship('Area')
    role = relationship('Role')

