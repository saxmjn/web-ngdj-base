# django-base
This project is not an Introduction to Django. To get the most out of it, you should be familiar with Django.
This project comprises of following microservices/micro-features built on top of Django Framework

1. JWT Authentication with Phone, Email, Google, Facebook
2. Celery and Redis based contacts upload
3. Real Time Chat
4. Notification feed
5. Elastic Search based text and tag search engine

## JWT AUTH
JWT stand for JSON Web Token and it is an authentication strategy used by client/server applications where the client is a Web application using JavaScript or mobile platforms like Android or iOS.

In this app we are going to explore the specifics of JWT authentication and how we have integrated the same withing Django to use either of Phone, Email, Google or Facebook auth.

A JWT Token looks something like this xxxxx.yyyyy.zzzzz, those are three distinctive parts that compose a JWT:
```
header.payload.signature
```

#### Libraries Used:
1. djangorestframework==3.9.4
2. djangorestframework-jwt==1.11.0
3. PyJWT==1.7.1


#### Features:
1. User Signup/Signin with Email
2. User Signup/Signin with Phone
3. Forgot Password
4. Change Password
5. Update Email
6. Update Phone

## CONTACTS AND INVITE BUILT WITH CELERY

#### Libraries used:
1. celery==4.2.2
2. redis==3.3.4

#### Development:
##### 1. Setup for Celery in Django

> Code snippet from app/celery.py
```
from __future__ import absolute_import
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery()

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

```

> Code snippet from app/settings.py
```
# -----------------------------
# REDIS
# -----------------------------
# redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
redis_url = get_from_environment('REDISCLOUD_URL')

# -----------------------------
# CELERY
# -----------------------------
CELERY_BROKER_URL = get_from_environment('REDISCLOUD_URL')
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'application/text']

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_MAX_TASKS_PER_CHILD = 1

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
BROKER_POOL_LIMIT = 1  # Will decrease connection usage
BROKER_CONNECTION_TIMEOUT = 30  # May require a long timeout due to Linux DNS timeouts etc
BROKER_HEARTBEAT = 30  # Will detect stale connections faster
CELERY_SEND_EVENTS = False  # Will not create celeryev.* queues
CELERY_EVENT_QUEUE_EXPIRES = 86400 * 14  # Will delete all celeryev. queues without consumers after 1 minute.
DEFAULT_CACHE_EXPIRE = 60
```


##### 2. Defining Django Models
> Code snippet from contacts/models.py
```
class UserContact(models.Model):
    user = models.ForeignKey(User, db_index=True)
    contact = models.ForeignKey(User, null=True, related_name="user_contact")
    source = models.CharField(max_length=10, choices=constants.imported_contact_sources_choices)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, db_index=True, null=True)
    phone_code = models.CharField(max_length=5, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=10, choices=constants.user_contact_states_choices, default='0')
    block_invites = models.BooleanField(default=False)
    registered = models.BooleanField(default=False)
    invited_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    
    ....
    
    @staticmethod
    def create(user, source, first_name=None, last_name='', phone=None, email=None):
    
    ....
    
    @staticmethod
    def state_transition(invitor, invitee):
    
    ....
    
    @staticmethod
    def get_contacts(user, state=None, offset=None):
    
    ....
    
    @staticmethod
    def invite_contacts(user, invite_all=False, deselectd_ids=[], selected_ids=[]):
    
    ....
```

##### 3. Creating a Celery Task

> Code snippet from contacts/tasks.py
```
def import_contacts_from_phone(user_id, contacts=[]):
    user = User.objects.get(id=user_id)
    record = models.UserContactsImport.objects.get_or_create(user=user)[0]
    record.phone_import_recorded = False
    record.save()

    for contact in contacts:
        print(contact)
        try:
            models.UserContact.create(user=user, source='PHONE', first_name=contact['name'], phone=contact['phone'])
        except Exception as e:
            print(e)

    record.phone_import_recorded = True
    record.save()
    firebase.contacts_upload_trigger(to_user=user)
    return True
```
##### 4. Writing APIs and defining end points

> Code snippet from contacts/api_urls.py
```
urlpatterns = [
    url(r'^import/$', rest_views.import_contacts),
    url(r'^phone-import-recorded/$', rest_views.check_phone_import_recorded),
]
```

##### 5. Preparing for server

> Code snippet from Procfile
```
web: gunicorn commune.wsgi --log-file -
worker: celery worker --app=app.celery.app
```
Here 2nd line 3rd **app** is the actual name of your Django app. In our case its call **app** :)
