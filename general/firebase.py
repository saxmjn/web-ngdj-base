import firebase_admin
from commune.settings import get_path, get_from_environment
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import messaging

cred = credentials.Certificate(get_path('general/comune-a5687-firebase-adminsdk-9fjn7-f3f23ed6e6.json'))
firebase_ins = firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})


def get_users():
    firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
    db = firestore.client()
    docs = db.collection(u'users').get()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))


def setup_user_on_firebase(user):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
        db = firestore.client()
        user_id = str(user.id)
        db.collection('presence').document(user_id).set({'online': True})
        db.collection('users').document(user_id).set({'username': user.username})
        db.collection('users-external-event').document(user_id).set(
            {'notify_new_message': False, 'notify_general_count': 0, 'notify_contacts_upload': False})


def create_chat_on_firebase(firebase_id, user1_id, user2_id):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
        db = firestore.client()
        context = {'notify_new_message_to_user1': False, 'notify_new_message_to_user2': False,
                   'total_messages_count': 0, 'user1': user1_id, 'user2': user2_id}
        db.collection('chats').document(firebase_id).set(context)


def notify_new_msg_to_user(from_user, chat, count):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
        db = firestore.client()
        if from_user == chat.user1 and chat.firebase_id:
            db.collection('chats').document(chat.firebase_id).set({'total_messages_count': count}, merge=True)
            db.collection(u'users-external-event').document(str(chat.user2.id)).set({'notify_new_message': True},
                                                                                    merge=True)
            push_notification_trigger(to_user=chat.user2, from_user=from_user, type='NEW_MESSAGE',
                                      reference_id=chat.user1.id, reference_username=chat.user1.username)
        elif from_user == chat.user2 and chat.firebase_id:
            db.collection('chats').document(chat.firebase_id).set({'total_messages_count': count}, merge=True)
            db.collection(u'users-external-event').document(str(chat.user1.id)).set({'notify_new_message': True},
                                                                                    merge=True)
            push_notification_trigger(to_user=chat.user1, from_user=from_user, type='NEW_MESSAGE',
                                      reference_id=chat.user2.id, reference_username=chat.user2.username)


def notify_general_to_user(to_user, count):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
        db = firestore.client()
        db.collection(u'users-external-event').document(str(to_user.id)).set({'notify_general_count': count}, merge=True)


def contacts_upload_trigger(to_user):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
        db = firestore.client()
        db.collection(u'users-external-event').document(str(to_user.id)).set({'notify_contacts_upload': True}, merge=True)


def online_users():
    if not firebase_ins:
        firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
    db = firestore.client()
    docs = db.collection('presence').where(u'online', u'==', True).get()
    users = [int(doc.id) for doc in docs]
    return users


def push_notification_trigger(to_user, from_user=None, type='', reference_id='', reference_username=''):
    try:
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
        token = to_user.userprofile.device_token
        data = {'reference_type': type, 'reference_id': str(reference_id), 'reference_username': reference_username,
                'title': ''}
        if not token:
            return
        print(type)
        if type == 'NEW_MESSAGE':
            data['title'] = '{} sent you a new message'.format(from_user.first_name)
        elif type == 'NEW_FOLLOWER':
            data['title'] = '{} started following you'.format(from_user.first_name)
        elif type == 'NEW_COMMENT_ON_BROADCAST':
            data['title'] = '{} commented on your broadcast'.format(from_user.first_name)

        print(data)
        # noti = messaging.Notification(title=title)
        config = messaging.AndroidConfig(priority='high')
        msg = messaging.Message(data=data, token=token, android=config)
        print(msg)
        x = messaging.send(message=msg)
        print(x)
    except Exception as e:
        print(e)
        pass


def push_notification_trigger_to_topic(topic, from_user=None, type='', reference_id='', reference_username=''):
    try:
        if not topic:
            return

        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})

        data = {'reference_type': type, 'reference_id': str(reference_id), 'reference_username': reference_username,
                'title': ''}
        print(data)
        config = messaging.AndroidConfig(priority='high')

        if type == 'NEW_BROADCAST':
            data['title'] = '{} added a new broadcast'.format(from_user.first_name)

        msg = messaging.Message(data=data, topic=topic, android=config)

        print(msg)
        x = messaging.send(message=msg)
        print(x)
    except Exception as e:
        print(e)
        pass


def subscribe_to_topic(topic, user):
    if not firebase_ins:
        firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
    token = user.userprofile.device_token
    if token:
        messaging.subscribe_to_topic(tokens=[token], topic=topic, app=None)


def unsubscribe_from_topic(topic, user):
    if not firebase_ins:
        firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
    token = user.userprofile.device_token
    if token:
        messaging.unsubscribe_from_topic(tokens=[token], topic=topic, app=None)


def sample_push():
    if not firebase_ins:
        firebase_admin.initialize_app(cred, {'projectId': 'comune-a5687'})
    data = {}
    token = 'dRrqElTiZhg:APA91bG-u_6j355pW-RC5XzemAEMnsSCvyPEp-DoQc6l3qk3TgSyfQGXKmumGsAZoI7qtp_f1Kk9KPEdcRBgXBtoiv3cc1GRZXO9jJQPcUdDfXWdpJPkrAEKQEJkoeMog4VxxcNqonmr'
    title = 'sent you a new message'
    noti = messaging.Notification(title=title)
    msg = messaging.Message(data=data, token=token, notification=noti)
    x = messaging.send(message=msg)
    print(x)
