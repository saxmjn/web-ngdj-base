
## REAL TIME CHAT
In this part I will talk about developing a real time chat. You can check the chat working in this video.
#### Features of Chat App:
* Chat is based on channel which comprise of two participants
* Participants can send each other messages in text, file and image formats
* Participants can take actions like delete and forward a message

#### Libraries Used:
* Firebase
* AWS S3

#### Development:
##### 1. Defining a django models
Our Chat architecture comprises of a Chat Model which is a channel between two participants. And Message Model which are messages sent across the Chat.

> Code snippet from chat/models.py
```
class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name='primary_user', null=False, blank=False)
    user2 = models.ForeignKey(User, related_name='secondary_user', null=False, blank=False)
    last_msg_read_by_user1 = models.BooleanField(default=True)
    last_msg_read_by_user2 = models.BooleanField(default=True)
    firebase_id = models.CharField(max_length=250, null=True, blank=True)
    started = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)
```

Each message object has an associated Foreignkey to Chat & User username, timestamp, and the actual message text.
> Code snippet from chat/models.py
```
class Message(models.Model):
    class Meta:
        get_latest_by = "message_number"
        verbose_name = "Message"

    created = models.DateTimeField(auto_now_add=True, editable=False)
    from_user = models.ForeignKey(User, related_name='from_user', null=False, blank=False)
    type = models.CharField(choices=constants.chat_type_states_choices, max_length=30,default=constants.chat_type_states['TEXT'])
    text = models.TextField(null=True, blank=True)
    file = models.ForeignKey('general.File', null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    message_number = models.BigIntegerField(default=0)
    chat = models.ForeignKey(Chat, null=True)
    reference_type = models.CharField(choices=constants.reference_type_states_choices, max_length=500, null=True,blank=True)
    reference_id = models.CharField(max_length=500, null=True, blank=True)
    action = models.CharField(max_length=40, blank=True, null=True)
    action_params = models.TextField(blank=True, null=True)
```
##### 2. Putting Firebase endpoints
Before we dive into the the read and write operation to firebase, first of all create a model on firebase db that represent the scruture of chat message, such that our Chat collection on firebase looks like this

```
-chats
   - chatID
       - user1
       - user2
       - total_messages_count
       - last_message_timestamp
```
Here chatID (LowerUserId_HigherUserId) is the conversation node between User1 for ex: 108 and User2 for ex: 109 and is also set as firebase_id in Chat Model in Djnago

Our next step would be defining some write operations for Firebase.
> Code snippet from general/firebase.py
```
def create_chat_on_firebase(firebase_id, user1_id, user2_id):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': firebase_app})
        db = firestore.client()
        context = {'notify_new_message_to_user1': False, 'notify_new_message_to_user2': False,'total_messages_count': 0, 'user1': user1_id, 'user2': user2_id}
        db.collection('chats').document(firebase_id).set(context)

```
> Code snippet from general/firebase.py
```
def notify_new_msg_to_user(from_user, chat, count):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': firebase_app})
        db = firestore.client()
        if from_user == chat.user1 and chat.firebase_id:
            db.collection('chats').document(chat.firebase_id).set({'total_messages_count': count}, merge=True)
            db.collection(u'users-external-event').document(str(chat.user2.id)).set({'notify_new_message': True},merge=True)
            push_notification_trigger(to_user=chat.user2, from_user=from_user, type='NEW_MESSAGE',reference_id=chat.user1.id,reference_username=chat.user1.username)
        elif from_user == chat.user2 and chat.firebase_id:
            db.collection('chats').document(chat.firebase_id).set({'total_messages_count': count}, merge=True)
            db.collection(u'users-external-event').document(str(chat.user1.id)).set({'notify_new_message': True},merge=True)
            push_notification_trigger(to_user=chat.user1, from_user=from_user, type='NEW_MESSAGE',reference_id=chat.user2.id, reference_username=chat.user2.username)
```
##### 3. Writing REST APIs and defining endpoints

> Code snippet from chat/api_urls.py
```
urlpatterns = [
    url(r'^list/$', rest_views.get_chat_list),
    url(r'^create/(?P<member_id>[-\w\d]+)/$', rest_views.create_chat),
    url(r'^(?P<chat_id>[-\w\d]+)/$', rest_views.get_chat),
    url(r'^message/add/(?P<chat_id>[-\w\d]+)/', rest_views.add_message),
    url(r'^message/new/(?P<chat_id>[-\w\d]+)/', rest_views.get_new_message),
    url(r'message/old/(?P<chat_id>[-\w\d]+)/$', rest_views.get_old_message)
]
```