from pyramid.events import subscriber, BeforeRender
from worq.models.models import Notifications, UsersNotifications

@subscriber(BeforeRender)
def add_unread_count(event):
    request = event.get('request')
    if not request:
        return
    session = getattr(request, 'session', None)
    dbsession = getattr(request, 'dbsession', None)
    if not session or not dbsession:
        event['unread_count'] = 0
        return
    user_id = session.get('user_id')
    if not user_id:
        event['unread_count'] = 0
        return
    unread_count = (
        dbsession.query(Notifications)
        .join(UsersNotifications, UsersNotifications.noti_id == Notifications.id)
        .filter(
            UsersNotifications.user_id == user_id,
            Notifications.state_id == 4
        )
        .count()
    )
    event['unread_count'] = unread_count