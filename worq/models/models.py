# coding: utf-8
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Areas(Base):
    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True, server_default=text("nextval('areas_id_seq'::regclass)"))
    area = Column(String, nullable=False)

class Countries(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, server_default=text("nextval('countries_id_seq'::regclass)"))
    name = Column(String, nullable=False)

class Permissions(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('permissions_id_seq'::regclass)"))
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=False)

class Roles(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, server_default=text("nextval('roles_id_seq'::regclass)"))
    name = Column(String, nullable=False)

class States(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    state = Column(String(100), nullable=False)

class Statuses(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True, server_default=text("nextval('status_id_seq'::regclass)"))
    status_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

class TaskPriorities(Base):
    __tablename__ = 'task_priorities'

    id = Column(Integer, primary_key=True, server_default=text("nextval('task_priorities_id_seq'::regclass)"))
    priority = Column(String(100), nullable=False)

class Types(Base):
    __tablename__ = 'types'

    id = Column(Integer, primary_key=True, server_default=text("nextval('types_id_seq'::regclass)"))
    type = Column(String(100), nullable=False)
    active = Column(Boolean, nullable=False)

class Notifications(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, server_default=text("nextval('notifications_id_seq'::regclass)"))
    type_id = Column(ForeignKey('types.id'), nullable=False)
    date = Column(Date, nullable=False)
    state = Column(String, nullable=False)

    type = relationship('Types')

class Projects(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, server_default=text("nextval('projects_id_seq'::regclass)"))
    state_id = Column(ForeignKey('states.id'), nullable=False)
    name = Column(String(200), nullable=False)
    startdate = Column(Date, nullable=False)
    enddate = Column(Date, nullable=False)
    creationdate = Column(Date, nullable=False)

    state = relationship('States')

class RolesPermissions(Base):
    __tablename__ = 'roles_permissions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('roles_permissions_id_seq'::regclass)"))
    role_id = Column(ForeignKey('roles.id'), nullable=False)
    permission_id = Column(ForeignKey('permissions.id'), nullable=False)

    permission = relationship('Permissions')
    role = relationship('Roles')

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_id_seq'::regclass)"))
    country_id = Column(ForeignKey('countries.id'))
    role_id = Column(ForeignKey('roles.id'), nullable=False)
    area_id = Column(ForeignKey('areas.id'))
    name = Column(String(100))
    tel = Column(String(20))
    email = Column(String(100), nullable=False)
    passw = Column(String(100), nullable=False)

    area = relationship('Areas')
    country = relationship('Countries')
    role = relationship('Roles')

class Actions(Base):
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, server_default=text("nextval('actions_id_seq'::regclass)"))
    type_id = Column(ForeignKey('types.id'), nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    project_id = Column(ForeignKey('projects.id'), nullable=False)
    date = Column(DateTime, nullable=False)

    project = relationship('Projects')
    type = relationship('Types')
    user = relationship('Users')

class Chats(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, server_default=text("nextval('chats_id_seq'::regclass)"))
    project_id = Column(ForeignKey('projects.id'), nullable=False)
    creationdate = Column(Date, nullable=False)

    project = relationship('Projects')

class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, server_default=text("nextval('files_id_seq'::regclass)"))
    uploaded_by = Column(ForeignKey('users.id'))
    filename = Column(String(200))
    filepath = Column(Text, nullable=False)
    uploaded_at = Column(DateTime(True))

    user = relationship('Users')

class ProjectNotifications(Base):
    __tablename__ = 'project_notifications'

    id = Column(Integer, primary_key=True, server_default=text("nextval('project_notifications_id_seq'::regclass)"))
    project_id = Column(ForeignKey('projects.id'), nullable=False)
    noti_id = Column(ForeignKey('notifications.id'), nullable=False)

    noti = relationship('Notifications')
    project = relationship('Projects')

class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, server_default=text("nextval('tasks_id_seq'::regclass)"))
    project_id = Column(ForeignKey('projects.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    creation_date = Column(DateTime, nullable=False)
    finished_date = Column(DateTime)
    due_date = Column(DateTime)
    priority_id = Column(ForeignKey('task_priorities.id'), nullable=False)
    status_id = Column(ForeignKey('status.id'), nullable=False)

    priority = relationship('TaskPriorities')
    project = relationship('Projects')
    status = relationship('Statuses')

class UsersNotifications(Base):
    __tablename__ = 'users_notifications'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_notifications_id_seq'::regclass)"))
    noti_id = Column(ForeignKey('notifications.id'), nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)

    noti = relationship('Notifications')
    user = relationship('Users')

class UsersProjects(Base):
    __tablename__ = 'users_projects'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_projects_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id'), nullable=False)
    project_id = Column(ForeignKey('projects.id'), nullable=False)
    role_id = Column(ForeignKey('roles.id'), nullable=False)

    project = relationship('Projects')
    role = relationship('Roles')
    user = relationship('Users')

class ChatsMessages(Base):
    __tablename__ = 'chats_messages'

    id = Column(Integer, primary_key=True, server_default=text("nextval('chats_messages_id_seq'::regclass)"))
    chat_id = Column(ForeignKey('chats.id'), nullable=False)
    sender_id = Column(ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    sent_time = Column(DateTime(True), nullable=False)

    chat = relationship('Chats')
    sender = relationship('Users')

class Requests(Base):
    __tablename__ = 'requests'

    id = Column(Integer, primary_key=True, server_default=text("nextval('requests_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id'), nullable=False)
    project_id = Column(ForeignKey('projects.id'), nullable=False)
    ex_user = Column(ForeignKey('users.id'))
    task_id = Column(ForeignKey('tasks.id'))
    status_id = Column(ForeignKey('status.id'), nullable=False)
    accepted_by = Column(ForeignKey('users.id'))
    rejected_by = Column(ForeignKey('users.id'))
    action_type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    request_date = Column(DateTime(True), nullable=False)

    user = relationship('Users', primaryjoin='Requests.accepted_by == Users.id')
    user1 = relationship('Users', primaryjoin='Requests.ex_user == Users.id')
    project = relationship('Projects')
    user2 = relationship('Users', primaryjoin='Requests.rejected_by == Users.id')
    status = relationship('Statuses')
    task = relationship('Tasks')
    user3 = relationship('Users', primaryjoin='Requests.user_id == Users.id')

class TaskFiles(Base):
    __tablename__ = 'task_files'

    id = Column(Integer, primary_key=True, server_default=text("nextval('task_files_id_seq'::regclass)"))
    file_id = Column(ForeignKey('files.id'), nullable=False)
    task_id = Column(ForeignKey('tasks.id'), nullable=False)

    file = relationship('Files')
    task = relationship('Tasks')

class TaskRequirements(Base):
    __tablename__ = 'task_requirements'

    id = Column(Integer, primary_key=True, server_default=text("nextval('task_requirements_id_seq'::regclass)"))
    task_id = Column(ForeignKey('tasks.id'), nullable=False)
    requirement = Column(String(250), nullable=False)
    is_completed = Column(Boolean, nullable=False)

    task = relationship('Tasks')

class UsersTasks(Base):
    __tablename__ = 'users_tasks'

    id = Column(Integer, primary_key=True, server_default=text("nextval('users_tasks_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id'), nullable=False)
    task_id = Column(ForeignKey('tasks.id'), nullable=False)

    task = relationship('Tasks')
    user = relationship('Users')
class ChatFiles(Base):
    __tablename__ = 'chat_files'

    id = Column(Integer, primary_key=True, server_default=text("nextval('chat_files_id_seq'::regclass)"))
    chat_message_id = Column(ForeignKey('chats_messages.id'), nullable=False)
    file_id = Column(ForeignKey('files.id'), nullable=False)

    chat_message = relationship('ChatsMessages')
    file = relationship('Files')
