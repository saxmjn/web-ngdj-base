from django.conf.urls import url
from . import rest_views


urlpatterns = [
    url(r'^import/$', rest_views.import_contacts),
    url(r'^phone-import-recorded/$', rest_views.check_phone_import_recorded),
]