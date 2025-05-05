from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime

class Base(DeclarativeBase):
    pass


class Areas(Base):
    __tablename__ = 'areas'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='areas_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    area: Mapped[str] = mapped_column(String)

    users: Mapped[List['Users']] = relationship('Users', back_populates='area')


class Countries(Base):
    __tablename__ = 'countries'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='countries_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    users: Mapped[List['Users']] = relationship('Users', back_populates='country')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    users: Mapped[List['Users']] = relationship('Users', back_populates='role')


class States(Base):
    __tablename__ = 'states'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='states_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(100))

    projects: Mapped[List['Projects']] = relationship('Projects', back_populates='state')


class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='status_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)

    requests: Mapped[List['Requests']] = relationship('Requests', back_populates='status')


class Types(Base):
    __tablename__ = 'types'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='types_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean)

    notifications: Mapped[List['Notifications']] = relationship('Notifications', back_populates='type')
    actions: Mapped[List['Actions']] = relationship('Actions', back_populates='type')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['type_id'], ['types.id'], name='type'),
        PrimaryKeyConstraint('id', name='notifications_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime.date] = mapped_column(Date)
    state: Mapped[str] = mapped_column(String)

    type: Mapped['Types'] = relationship('Types', back_populates='notifications')
    project_notifications: Mapped[List['ProjectNotifications']] = relationship('ProjectNotifications', back_populates='noti')
    users_notifications: Mapped[List['UsersNotifications']] = relationship('UsersNotifications', back_populates='noti')


class Projects(Base):
    __tablename__ = 'projects'
    __table_args__ = (
        ForeignKeyConstraint(['state_id'], ['states.id'], name='state_fk'),
        PrimaryKeyConstraint('id', name='projects_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(200))
    startdate: Mapped[datetime.date] = mapped_column(Date)
    enddate: Mapped[datetime.date] = mapped_column(Date)
    creationdate: Mapped[datetime.date] = mapped_column(Date)

    state: Mapped['States'] = relationship('States', back_populates='projects')
    actions: Mapped[List['Actions']] = relationship('Actions', back_populates='project')
    chats: Mapped[List['Chats']] = relationship('Chats', back_populates='project')
    project_notifications: Mapped[List['ProjectNotifications']] = relationship('ProjectNotifications', back_populates='project')
    tasks: Mapped[List['Tasks']] = relationship('Tasks', back_populates='project')
    users_projects: Mapped[List['UsersProjects']] = relationship('UsersProjects', back_populates='project')
    requests: Mapped[List['Requests']] = relationship('Requests', back_populates='project')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['area_id'], ['areas.id'], name='area_fk'),
        ForeignKeyConstraint(['country_id'], ['countries.id'], name='country_fk'),
        ForeignKeyConstraint(['role_id'], ['roles.id'], name='role_fk'),
        PrimaryKeyConstraint('id', name='users_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int] = mapped_column(Integer)
    role_id: Mapped[int] = mapped_column(Integer)
    area_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    tel: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(100))
    passw: Mapped[str] = mapped_column(String(100))

    area: Mapped['Areas'] = relationship('Areas', back_populates='users')
    country: Mapped['Countries'] = relationship('Countries', back_populates='users')
    role: Mapped['Roles'] = relationship('Roles', back_populates='users')
    actions: Mapped[List['Actions']] = relationship('Actions', back_populates='user')
    files: Mapped[List['Files']] = relationship('Files', back_populates='users')
    users_notifications: Mapped[List['UsersNotifications']] = relationship('UsersNotifications', back_populates='user')
    users_projects: Mapped[List['UsersProjects']] = relationship('UsersProjects', back_populates='user')
    chats_messages: Mapped[List['ChatsMessages']] = relationship('ChatsMessages', back_populates='sender')
    requests: Mapped[List['Requests']] = relationship('Requests', foreign_keys='[Requests.accepted_by]', back_populates='users')
    requests_: Mapped[List['Requests']] = relationship('Requests', foreign_keys='[Requests.ex_user]', back_populates='users_')
    requests1: Mapped[List['Requests']] = relationship('Requests', foreign_keys='[Requests.rejected_by]', back_populates='users1')
    requests2: Mapped[List['Requests']] = relationship('Requests', foreign_keys='[Requests.user_id]', back_populates='user')
    users_tasks: Mapped[List['UsersTasks']] = relationship('UsersTasks', back_populates='user')


class Actions(Base):
    __tablename__ = 'actions'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        ForeignKeyConstraint(['type_id'], ['types.id'], name='type'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='actions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    project_id: Mapped[int] = mapped_column(Integer)
    date: Mapped[datetime.datetime] = mapped_column(DateTime)

    project: Mapped['Projects'] = relationship('Projects', back_populates='actions')
    type: Mapped['Types'] = relationship('Types', back_populates='actions')
    user: Mapped['Users'] = relationship('Users', back_populates='actions')


class Chats(Base):
    __tablename__ = 'chats'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_fk'),
        PrimaryKeyConstraint('id', name='chats_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer)
    creationdate: Mapped[datetime.date] = mapped_column(Date)

    project: Mapped['Projects'] = relationship('Projects', back_populates='chats')
    chats_messages: Mapped[List['ChatsMessages']] = relationship('ChatsMessages', back_populates='chat')


class Files(Base):
    __tablename__ = 'files'
    __table_args__ = (
        ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='users_fk'),
        PrimaryKeyConstraint('id', name='files_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uploaded_by: Mapped[int] = mapped_column(Integer)
    filename: Mapped[str] = mapped_column(String(200))
    filepath: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime(True))

    users: Mapped['Users'] = relationship('Users', back_populates='files')
    task_files: Mapped[List['TaskFiles']] = relationship('TaskFiles', back_populates='file')
    chat_files: Mapped[List['ChatFiles']] = relationship('ChatFiles', back_populates='file')


class ProjectNotifications(Base):
    __tablename__ = 'project_notifications'
    __table_args__ = (
        ForeignKeyConstraint(['noti_id'], ['notifications.id'], name='notis'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        PrimaryKeyConstraint('id', name='project_notifications_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer)
    noti_id: Mapped[int] = mapped_column(Integer)

    noti: Mapped['Notifications'] = relationship('Notifications', back_populates='project_notifications')
    project: Mapped['Projects'] = relationship('Projects', back_populates='project_notifications')


class Tasks(Base):
    __tablename__ = 'tasks'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project'),
        PrimaryKeyConstraint('id', name='tasks_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    creation_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    started_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    finished_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    project: Mapped['Projects'] = relationship('Projects', back_populates='tasks')
    requests: Mapped[List['Requests']] = relationship('Requests', back_populates='task')
    task_files: Mapped[List['TaskFiles']] = relationship('TaskFiles', back_populates='task')
    users_tasks: Mapped[List['UsersTasks']] = relationship('UsersTasks', back_populates='task')


class UsersNotifications(Base):
    __tablename__ = 'users_notifications'
    __table_args__ = (
        ForeignKeyConstraint(['noti_id'], ['notifications.id'], name='notis'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='users_notifications_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    noti_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)

    noti: Mapped['Notifications'] = relationship('Notifications', back_populates='users_notifications')
    user: Mapped['Users'] = relationship('Users', back_populates='users_notifications')


class UsersProjects(Base):
    __tablename__ = 'users_projects'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['projects.id'], name='project_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user_fk'),
        PrimaryKeyConstraint('id', name='users_projects_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    project_id: Mapped[int] = mapped_column(Integer)

    project: Mapped['Projects'] = relationship('Projects', back_populates='users_projects')
    user: Mapped['Users'] = relationship('Users', back_populates='users_projects')


class ChatsMessages(Base):
    __tablename__ = 'chats_messages'
    __table_args__ = (
        ForeignKeyConstraint(['chat_id'], ['chats.id'], name='chat_fk'),
        ForeignKeyConstraint(['sender_id'], ['users.id'], name='sender_id'),
        PrimaryKeyConstraint('id', name='chats_messages_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer)
    sender_id: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    sent_time: Mapped[datetime.datetime] = mapped_column(DateTime(True))

    chat: Mapped['Chats'] = relationship('Chats', back_populates='chats_messages')
    sender: Mapped['Users'] = relationship('Users', back_populates='chats_messages')
    chat_files: Mapped[List['ChatFiles']] = relationship('ChatFiles', back_populates='chat_message')


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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    project_id: Mapped[int] = mapped_column(Integer)
    status_id: Mapped[int] = mapped_column(Integer)
    action_type: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(Text)
    request_date: Mapped[datetime.datetime] = mapped_column(DateTime(True))
    ex_user: Mapped[Optional[int]] = mapped_column(Integer)
    task_id: Mapped[Optional[int]] = mapped_column(Integer)
    accepted_by: Mapped[Optional[int]] = mapped_column(Integer)
    rejected_by: Mapped[Optional[int]] = mapped_column(Integer)

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[accepted_by], back_populates='requests')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[ex_user], back_populates='requests_')
    project: Mapped['Projects'] = relationship('Projects', back_populates='requests')
    users1: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[rejected_by], back_populates='requests1')
    status: Mapped['Status'] = relationship('Status', back_populates='requests')
    task: Mapped[Optional['Tasks']] = relationship('Tasks', back_populates='requests')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='requests2')


class TaskFiles(Base):
    __tablename__ = 'task_files'
    __table_args__ = (
        ForeignKeyConstraint(['file_id'], ['files.id'], name='file_fk'),
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task_fk'),
        PrimaryKeyConstraint('id', name='task_files_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_id: Mapped[int] = mapped_column(Integer)
    task_id: Mapped[int] = mapped_column(Integer)

    file: Mapped['Files'] = relationship('Files', back_populates='task_files')
    task: Mapped['Tasks'] = relationship('Tasks', back_populates='task_files')


class UsersTasks(Base):
    __tablename__ = 'users_tasks'
    __table_args__ = (
        ForeignKeyConstraint(['task_id'], ['tasks.id'], name='task'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='user'),
        PrimaryKeyConstraint('id', name='users_tasks_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    task_id: Mapped[int] = mapped_column(Integer)

    task: Mapped['Tasks'] = relationship('Tasks', back_populates='users_tasks')
    user: Mapped['Users'] = relationship('Users', back_populates='users_tasks')


class ChatFiles(Base):
    __tablename__ = 'chat_files'
    __table_args__ = (
        ForeignKeyConstraint(['chat_message_id'], ['chats_messages.id'], name='chat_messages_fk'),
        ForeignKeyConstraint(['file_id'], ['files.id'], name='file_fk'),
        PrimaryKeyConstraint('id', name='chat_files_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_message_id: Mapped[int] = mapped_column(Integer)
    file_id: Mapped[int] = mapped_column(Integer)

    chat_message: Mapped['ChatsMessages'] = relationship('ChatsMessages', back_populates='chat_files')
    file: Mapped['Files'] = relationship('Files', back_populates='chat_files')
