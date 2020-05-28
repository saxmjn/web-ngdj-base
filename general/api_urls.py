from django.conf.urls import url
from . import rest_views


urlpatterns = [
    url(r'^otp/', rest_views.get_otp),
    url(r'^file/store/', rest_views.post_file),
    url(r'^category/list/', rest_views.get_categories),
    url(r'^city/list/', rest_views.get_cities),
    url(r'^contact-query/', rest_views.post_contact_query),
    url(r'^newsletter-subscriber/', rest_views.post_newsletter_subscriber),
    url(r'analytics/datetime-vs-users/$', rest_views.get_datetime_vs_users),
    url(r'analytics/last-opened-info/$', rest_views.get_last_opened_info),
]