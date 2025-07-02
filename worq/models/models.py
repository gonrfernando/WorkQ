from typing import List, Optional

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint,
    String, Text, text, Column
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Areas(Base):
    __tablename__ = 'areas'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='areas_pkey'),
    )

    id = Column(Integer, primary_key=True)
    area = Column(String)

    users = relationship('Users', back_populates='area')

class Countries(Base):
    __tablename__ = 'countries'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='countries_pkey'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String)

    users = relationship('Users', back_populates='country')

class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String)

    users = relationship('Users', back_populates='role')

class States(Base):
    __tablename__ = 'states'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='states_pkey'),
    )

    id = Column(Integer, primary_key=True)
    state = Column(String(100))

    notifications = relationship('Notifications', back_populates='state')
    projects = relationship('Projects', back_populates='state')

class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='status_pkey'),
    )

    id = Column(Integer, primary_key=True)
    status_name = Column(String(100))
    description = Column(Text)

    tasks = relationship('Tasks', back_populates='status')
    requests = relationship('Requests', back_populates='status')

class TaskPriorities(Base):
    __tablename__ = 'task_priorities'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='task_priorities_pkey'),
    )

    id = Column(Integer, primary_key=True)
    priority = Column(String(100))

    tasks = relationship('Tasks', back_populates='priority')

class Types(Base):
    __tablename__ = 'types'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='types_pkey'),
    )

    id = Column(Integer, primary_key=True)
    type = Column(String(100))
    active = Column(Boolean)

    notifications = relationship('Notifications', back_populates='type')
    actions = relationship('Actions', back_populates='type')

class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['state_id'], ['states.id'], name='state_fk'),
        ForeignKeyConstraint(['type_id'], ['types.id'], name='type'),
        PrimaryKeyConstraint('id', name='notifications_pkey')
    )

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer)
    date = Column(DateTime)
    state_id = Column(Integer)

    state = relationship('States', back_populates='notifications')
    type = relationship('Types', back_populates='notifications')
    users_notifications = relationship('UsersNotifications', back_populates='noti')
    project_notifications = relationship('ProjectNotifications', back_populates='noti')

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['area_id'], ['areas.id'], name='area_fk'),
        ForeignKeyConstraint(['country_id'], ['countries.id'], name='country_fk'),
        ForeignKeyConstraint(['role_id'], ['roles.id'], name='role_fk'),
        PrimaryKeyConstraint('id', name='users_pkey')
    )

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer)
    email = Column(String(100))
    passw = Column(String(100))
    country_id = Column(Integer)
    area_id = Column(Integer)
    name = Column(String(100))
    tel = Column(String(20))

    area = relationship('Areas', back_populates='users')
    country = relationship('Countries', back_populates='users')
    role = relationship('Roles', back_populates='users')
    files = relationship('Files', back_populates='users')
    projects = relationship('Projects', back_populates='user')
    users_notifications = relationship('UsersNotifications', back_populates='user')
    actions = relationship('Actions', back_populates='user')
    icons = relationship('Icons', back_populates='user')
    tasks = relationship('Tasks', back_populates='users')
    users_projects = relationship('UsersProjects', foreign_keys='[UsersProjects.invited_by]', back_populates='users')
    users_projects_ = relationship('UsersProjects', foreign_keys='[UsersProjects.user_id]', back_populates='user')
    feedbacks = relationship('Feedbacks', back_populates='user', foreign_keys='Feedbacks.user_id')
    requests = relationship('Requests', foreign_keys='[Requests.accepted_by]', back_populates='users')
    requests_ = relationship('Requests', foreign_keys='[Requests.ex_user]', back_populates='users_')
    requests1 = relationship('Requests', foreign_keys='[Requests.rejected_by]', back_populates='users1')
    requests2 = relationship('Requests', foreign_keys='[Requests.user_id]', back_populates='user')
    users_tasks = relationship('UsersTasks', back_populates='user')
    users_feedbacks = relationship('UsersFeedbacks', back_populates='user')

class Files(Base):
    __tablename__ = 'files'
    __table_args__ = (
        ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='users_fk'),
        PrimaryKeyConstraint('id', name='files_pkey')
    )

    id = Column(Integer, primary_key=True)
    filepath = Column(Text)
    uploaded_by = Column(Integer)
    filename = Column(String(200))
    uploaded_at = Column(DateTime(True))

    users = relationship('Users', back_populates='files')
    icons = relationship('Icons', back_populates='file')
    task_files = relationship('TaskFiles', back_populates='file')

class Projects(Base):
    __tablename__ = 'projects'
    __table_args__ = (
        ForeignKeyConstraint(['state_id'], ['states.id'], name='state_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='projects_pkey')
    )

    id = Column(Integer, primary_key=True)
    state_id = Column(Integer)
    name = Column(String(200))
    startdate = Column(Date)
    enddate = Column(Date)
    creationdate = Column(Date)
    user_id = Column(Integer)

    state = relationship('States', back_populates='projects')
    user = relationship('Users', back_populates='projects')
    actions = relationship('Actions', back_populates='project')
    project_notifications = relationship('ProjectNotifications', back_populates='project')
    tasks = relationship('Tasks', back_populates='project')
    users_projects = relationship('UsersProjects', back_populates='project')
    requests = relationship('Requests', back_populates='project')

class UsersNotifications(Base):
    __tablename__ = 'users_notifications'
    __table_args__ = (
        ForeignKeyConstraint(['noti_id'], ['notifications.id'], name='notis'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='users_notifications_pkey')
    )

    id = Column(Integer, primary_key=True)
    noti_id = Column(Integer)
    user_id = Column(Integer)

    noti = relationship('Notifications', back_populates='users_notifications')
    user = relationship('Users', back_populates='users_notifications')

class Actions(Base):
    __tablename__ = 'actions'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        ForeignKeyConstraint(['type_id'], ['types.id'], name='type'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='actions_pkey')
    )

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer)
    user_id = Column(Integer)
    project_id = Column(Integer)
    date = Column(DateTime)

    project = relationship('Projects', back_populates='actions')
    type = relationship('Types', back_populates='actions')
    user = relationship('Users', back_populates='actions')

class Icons(Base):
    __tablename__ = 'icons'
    __table_args__ = (
        ForeignKeyConstraint(['file_id'], ['files.id'], name='file_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='icons_pkey')
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    file_id = Column(Integer)

    file = relationship('Files', back_populates='icons')
    user = relationship('Users', back_populates='icons')

class ProjectNotifications(Base):
    __tablename__ = 'project_notifications'
    __table_args__ = (
        ForeignKeyConstraint(['noti_id'], ['notifications.id'], name='notis'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        PrimaryKeyConstraint('id', name='project_notifications_pkey')
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    noti_id = Column(Integer)

    noti = relationship('Notifications', back_populates='project_notifications')
    project = relationship('Projects', back_populates='project_notifications')

class Tasks(Base):
    __tablename__ = 'tasks'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='user_fk'),
        ForeignKeyConstraint(['priority_id'], ['task_priorities.id'], name='priority_fk'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='tasks_status_id_fkey'),
        PrimaryKeyConstraint('id', name='tasks_pkey')
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    title = Column(String)
    description = Column(Text)
    creation_date = Column(DateTime)
    priority_id = Column(Integer)
    status_id = Column(Integer, server_default=text('1'))
    finished_date = Column(DateTime)
    deliver_date = Column(DateTime)
    created_by = Column(Integer)

    users = relationship('Users', back_populates='tasks')
    priority = relationship('TaskPriorities', back_populates='tasks')
    project = relationship('Projects', back_populates='tasks')
    status = relationship('Status', back_populates='tasks')
    requests = relationship('Requests', back_populates='task')
    task_files = relationship('TaskFiles', back_populates='task')
    task_requirements = relationship('TaskRequirements', back_populates='task')
    users_tasks = relationship('UsersTasks', back_populates='task')

class UsersProjects(Base):
    __tablename__ = 'users_projects'
    __table_args__ = (
        ForeignKeyConstraint(['invited_by'], ['users.id'], name='invited_fk'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='users_projects_pkey')
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    project_id = Column(Integer)
    invited_by = Column(Integer)

    users = relationship('Users', foreign_keys=[invited_by], back_populates='users_projects')
    project = relationship('Projects', back_populates='users_projects')
    user = relationship('Users', foreign_keys=[user_id], back_populates='users_projects_')

class Feedbacks(Base):
    __tablename__ = 'feedbacks'
    __table_args__ = (
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='feedbacks_pkey')
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer)
    comment = Column(Text)
    date = Column(DateTime)
    user_id = Column(Integer)

    user = relationship('Users', back_populates='feedbacks')
    users_feedbacks = relationship('UsersFeedbacks', back_populates='feedback')

class Requests(Base):
    __tablename__ = 'requests'
    __table_args__ = (
        ForeignKeyConstraint(['accepted_by'], ['users.id'], name='accepted_fk'),
        ForeignKeyConstraint(['ex_user'], ['users.id'], name='ex_fk'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_fk'),
        ForeignKeyConstraint(['rejected_by'], ['users.id'], name='rejected_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='status_fk'),
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='requests_pkey')
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    project_id = Column(Integer)
    status_id = Column(Integer)
    action_type = Column(String(50))
    reason = Column(Text)
    request_date = Column(DateTime(True))
    ex_user = Column(Integer)
    task_id = Column(Integer)
    accepted_by = Column(Integer)
    rejected_by = Column(Integer)

    users = relationship('Users', foreign_keys=[accepted_by], back_populates='requests')
    users_ = relationship('Users', foreign_keys=[ex_user], back_populates='requests_')
    project = relationship('Projects', back_populates='requests')
    users1 = relationship('Users', foreign_keys=[rejected_by], back_populates='requests1')
    status = relationship('Status', back_populates='requests')
    task = relationship('Tasks', back_populates='requests')
    user = relationship('Users', foreign_keys=[user_id], back_populates='requests2')

class TaskFiles(Base):
    __tablename__ = 'task_files'
    __table_args__ = (
        ForeignKeyConstraint(['file_id'], ['files.id'], name='file_fk'),
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task_fk'),
        PrimaryKeyConstraint('id', name='task_files_pkey')
    )

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer)
    task_id = Column(Integer)

    file = relationship('Files', back_populates='task_files')
    task = relationship('Tasks', back_populates='task_files')

class TaskRequirements(Base):
    __tablename__ = 'task_requirements'
    __table_args__ = (
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task_fk'),
        PrimaryKeyConstraint('id', name='task_requirements_pkey')
    )

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer)
    requirement = Column(String(250))
    is_completed = Column(Boolean)

    task = relationship('Tasks', back_populates='task_requirements')

class UsersTasks(Base):
    __tablename__ = 'users_tasks'
    __table_args__ = (
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='users_tasks_pkey')
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    task_id = Column(Integer)

    task = relationship('Tasks', back_populates='users_tasks')
    user = relationship('Users', back_populates='users_tasks')

class UsersFeedbacks(Base):
    __tablename__ = 'users_feedbacks'
    __table_args__ = (
        ForeignKeyConstraint(['feedback_id'], ['feedbacks.id'], name='feedback_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='users_feedbacks_pkey')
    )

    id = Column(Integer, primary_key=True)
    feedback_id = Column(Integer)
    user_id = Column(Integer)

    feedback = relationship('Feedbacks', back_populates='users_feedbacks')
    user = relationship('Users', back_populates='users_feedbacks')