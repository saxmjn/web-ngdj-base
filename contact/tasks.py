# Comment: uncomment after fixing
# from __future__ import absolute_import, unicode_literals
# from celery import shared_task
# from app.celery import app
# from django.contrib.auth.models import User
# from general import firebase

# from . import models


# @app.task
# def import_contacts_from_phone(user_id, contacts=[]):
#     user = User.objects.get(id=user_id)
#     record = models.UserContactsImport.objects.get_or_create(user=user)[0]
#     record.phone_import_recorded = False
#     record.save()

#     for contact in contacts:
#         print(contact)
#         try:
#             models.UserContact.create(user=user, source='PHONE', first_name=contact['name'], phone=contact['phone'])
#         except Exception as e:
#             print(e)

#     record.phone_import_recorded = True
#     record.save()
#     firebase.contacts_upload_trigger(to_user=user)
#     return True