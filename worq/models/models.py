from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Areas(Base):
    __tablename__ = 'areas'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='areas_pkey'),
    )

    id = Column(Integer)
    area = Column(String, nullable=False)

    users = relationship('Users', back_populates='area')


class Countries(Base):
    __tablename__ = 'countries'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='countries_pkey'),
    )

    id = Column(Integer)
    name = Column(String, nullable=False)

    users = relationship('Users', back_populates='country')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
    )

    id = Column(Integer)
    name = Column(String, nullable=False)

    users = relationship('Users', back_populates='role')


class States(Base):
    __tablename__ = 'states'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='states_pkey'),
    )

    id = Column(Integer)
    state = Column(String(100), nullable=False)

    projects = relationship('Projects', back_populates='state')


class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='status_pkey'),
    )

    id = Column(Integer)
    status_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    requests = relationship('Requests', back_populates='status')


class Types(Base):
    __tablename__ = 'types'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='types_pkey'),
    )

    id = Column(Integer)
    type = Column(String(100), nullable=False)
    active = Column(Boolean, nullable=False)

    notifications = relationship('Notifications', back_populates='type')
    actions = relationship('Actions', back_populates='type')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['type_id'], ['types.id'], name='type'),
        PrimaryKeyConstraint('id', name='notifications_pkey')
    )

    id = Column(Integer)
    type_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    state = Column(String, nullable=False)

    type = relationship('Types', back_populates='notifications')
    project_notifications = relationship('ProjectNotifications', back_populates='noti')
    users_notifications = relationship('UsersNotifications', back_populates='noti')


class Projects(Base):
    __tablename__ = 'projects'
    __table_args__ = (
        ForeignKeyConstraint(['state_id'], ['states.id'], name='state_fk'),
        PrimaryKeyConstraint('id', name='projects_pkey')
    )

    id = Column(Integer)
    state_id = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    startdate = Column(Date, nullable=False)
    enddate = Column(Date, nullable=False)
    creationdate = Column(Date, nullable=False)

    state = relationship('States', back_populates='projects')
    actions = relationship('Actions', back_populates='project')
    chats = relationship('Chats', back_populates='project')
    project_notifications = relationship('ProjectNotifications', back_populates='project')
    tasks = relationship('Tasks', back_populates='project')
    users_projects = relationship('UsersProjects', back_populates='project')
    requests = relationship('Requests', back_populates='project')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['area_id'], ['areas.id'], name='area_fk'),
        ForeignKeyConstraint(['country_id'], ['countries.id'], name='country_fk'),
        ForeignKeyConstraint(['role_id'], ['roles.id'], name='role_fk'),
        PrimaryKeyConstraint('id', name='users_pkey')
    )

    id = Column(Integer)
    country_id = Column(Integer, nullable=False)
    role_id = Column(Integer, nullable=False)
    area_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    tel = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    passw = Column(String(100), nullable=False)

    area = relationship('Areas', back_populates='users')
    country = relationship('Countries', back_populates='users')
    role = relationship('Roles', back_populates='users')
    actions = relationship('Actions', back_populates='user')
    files = relationship('Files', back_populates='users')
    users_notifications = relationship('UsersNotifications', back_populates='user')
    users_projects = relationship('UsersProjects', back_populates='user')
    chats_messages = relationship('ChatsMessages', back_populates='sender')
    requests = relationship('Requests', foreign_keys='[Requests.accepted_by]', back_populates='users')
    requests_ = relationship('Requests', foreign_keys='[Requests.ex_user]', back_populates='users_')
    requests1 = relationship('Requests', foreign_keys='[Requests.rejected_by]', back_populates='users1')
    requests2 = relationship('Requests', foreign_keys='[Requests.user_id]', back_populates='user')
    users_tasks = relationship('UsersTasks', back_populates='user')


class Actions(Base):
    __tablename__ = 'actions'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        ForeignKeyConstraint(['type_id'], ['types.id'], name='type'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='actions_pkey')
    )

    id = Column(Integer)
    type_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)

    project = relationship('Projects', back_populates='actions')
    type = relationship('Types', back_populates='actions')
    user = relationship('Users', back_populates='actions')


class Chats(Base):
    __tablename__ = 'chats'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_fk'),
        PrimaryKeyConstraint('id', name='chats_pkey')
    )

    id = Column(Integer)
    project_id = Column(Integer, nullable=False)
    creationdate = Column(Date, nullable=False)

    project = relationship('Projects', back_populates='chats')
    chats_messages = relationship('ChatsMessages', back_populates='chat')


class Files(Base):
    __tablename__ = 'files'
    __table_args__ = (
        ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='users_fk'),
        PrimaryKeyConstraint('id', name='files_pkey')
    )

    id = Column(Integer)
    uploaded_by = Column(Integer, nullable=False)
    filename = Column(String(200), nullable=False)
    filepath = Column(Text, nullable=False)
    uploaded_at = Column(DateTime(True), nullable=False)

    users = relationship('Users', back_populates='files')
    task_files = relationship('TaskFiles', back_populates='file')
    chat_files = relationship('ChatFiles', back_populates='file')


class ProjectNotifications(Base):
    __tablename__ = 'project_notifications'
    __table_args__ = (
        ForeignKeyConstraint(['noti_id'], ['notifications.id'], name='notis'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        PrimaryKeyConstraint('id', name='project_notifications_pkey')
    )

    id = Column(Integer)
    project_id = Column(Integer, nullable=False)
    noti_id = Column(Integer, nullable=False)

    noti = relationship('Notifications', back_populates='project_notifications')
    project = relationship('Projects', back_populates='project_notifications')


class Tasks(Base):
    __tablename__ = 'tasks'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        PrimaryKeyConstraint('id', name='tasks_pkey')
    )

    id = Column(Integer)
    project_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    creation_date = Column(DateTime, nullable=False)
    started_date = Column(DateTime, nullable=False)
    finished_date = Column(DateTime)

    project = relationship('Projects', back_populates='tasks')
    requests = relationship('Requests', back_populates='task')
    task_files = relationship('TaskFiles', back_populates='task')
    task_requirements = relationship('TaskRequirements', back_populates='task')
    users_tasks = relationship('UsersTasks', back_populates='task')


class UsersNotifications(Base):
    __tablename__ = 'users_notifications'
    __table_args__ = (
        ForeignKeyConstraint(['noti_id'], ['notifications.id'], name='notis'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='users_notifications_pkey')
    )

    id = Column(Integer)
    noti_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    noti = relationship('Notifications', back_populates='users_notifications')
    user = relationship('Users', back_populates='users_notifications')


class UsersProjects(Base):
    __tablename__ = 'users_projects'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='users_projects_pkey')
    )

    id = Column(Integer)
    user_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)

    project = relationship('Projects', back_populates='users_projects')
    user = relationship('Users', back_populates='users_projects')


class ChatsMessages(Base):
    __tablename__ = 'chats_messages'
    __table_args__ = (
        ForeignKeyConstraint(['chat_id'], ['chats.id'], name='chat_fk'),
        ForeignKeyConstraint(['sender_id'], ['users.id'], name='sender_id'),
        PrimaryKeyConstraint('id', name='chats_messages_pkey')
    )

    id = Column(Integer)
    chat_id = Column(Integer, nullable=False)
    sender_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    sent_time = Column(DateTime(True), nullable=False)

    chat = relationship('Chats', back_populates='chats_messages')
    sender = relationship('Users', back_populates='chats_messages')
    chat_files = relationship('ChatFiles', back_populates='chat_message')


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

    id = Column(Integer)
    user_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)
    status_id = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    request_date = Column(DateTime(True), nullable=False)
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

    id = Column(Integer)
    file_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)

    file = relationship('Files', back_populates='task_files')
    task = relationship('Tasks', back_populates='task_files')


class TaskRequirements(Base):
    __tablename__ = 'task_requirements'
    __table_args__ = (
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task_fk'),
        PrimaryKeyConstraint('id', name='task_requirements_pkey')
    )

    id = Column(Integer)
    task_id = Column(Integer, nullable=False)
    requirement = Column(String(250), nullable=False)
    is_completed = Column(Boolean, nullable=False)

    task = relationship('Tasks', back_populates='task_requirements')


class UsersTasks(Base):
    __tablename__ = 'users_tasks'
    __table_args__ = (
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='users_tasks_pkey')
    )

    id = Column(Integer)
    user_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)

    task = relationship('Tasks', back_populates='users_tasks')
    user = relationship('Users', back_populates='users_tasks')


class ChatFiles(Base):
    __tablename__ = 'chat_files'
    __table_args__ = (
        ForeignKeyConstraint(['chat_message_id'], ['chats_messages.id'], name='chat_messages_fk'),
        ForeignKeyConstraint(['file_id'], ['files.id'], name='file_fk'),
        PrimaryKeyConstraint('id', name='chat_files_pkey')
    )

    id = Column(Integer)
    chat_message_id = Column(Integer, nullable=False)
    file_id = Column(Integer, nullable=False)

    chat_message = relationship('ChatsMessages', back_populates='chat_files')
    file = relationship('Files', back_populates='chat_files')