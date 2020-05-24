from django.db import models
from django.conf import settings
# PROJECT
from app import constants, constants_app
from app import _firebase as firebase

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "authe.User")

# Create your models here.

class Notification(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    sender = models.ForeignKey(AUTH_USER_MODEL, related_name="notification_sender", on_delete=models.CASCADE)
    type = models.CharField(choices=constants.notification_type_choices, max_length=500, null=True,
                            blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    reference_id = models.CharField(max_length=500, null=True, blank=True)
    reference_type = models.CharField(choices=constants.notification_reference_choices, max_length=500, null=True,
                                      blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    @classmethod
    def new_follower(cls, connection):
        if connection.active:
            user = connection.user
            sender = connection.follower
            type = 'NEW_FOLLOWER'
            title = '{} has started following you'.format(sender.first_name)
            cls.objects.create(user=user, sender=sender, type=type, title=title)
            total_count = cls.objects.filter(user=user).count()
            firebase.notify_general_to_user(to_user=user, count=total_count)
            firebase.push_notification_trigger(to_user=user, from_user=sender, type='NEW_FOLLOWER', reference_id=sender.id, reference_username=sender.username)

    @classmethod
    def get_notifications(cls, user, offset=0):
        limit = 10
        offset = int(offset)
        total_count = cls.objects.filter(user=user).count()
        if offset == 0:
            user.userprofile.read_notification_count = total_count
            user.userprofile.save()
        notifications = cls.objects.filter(user=user).order_by('-created')[offset:offset + limit]
        read_count = user.userprofile.read_notification_count
        data = {'notifications': notifications, 'total_count': total_count, 'read_count': read_count}
        return data
