from django.conf.urls import url, include
from . import rest_views


urlpatterns = [
    url(r'phone-verification/$', rest_views.check_phone_verification),
    url(r'phone-update/$', rest_views.update_phone),
    url(r'email-update/$', rest_views.update_email),
    #
    url(r'^info/$', rest_views.get_user),
    #
    url(r'^tags/list/$', rest_views.get_user_tags),
    #
    url(r'^list/$', rest_views.get_all_users),
    url(r'^selected/list/$', rest_views.get_users_suggestion),
    url(r'^category/list/$', rest_views.get_users_for_categories),
    url(r'^profile/public/(?P<username>[-\w\d]+)/$', rest_views.get_user_profile, name='user_basic_profile_api'),
    url(r'^profile/private/$', rest_views.UserProfileView.as_view(), name='user_detail_profile_api'),
    url(r'^admin/$', rest_views.AdminUserProfileView.as_view(), name='admin_user_detail_profile_api'),
    url(r'suggestion/list/$', rest_views.get_suggestions_list),
    url(r'connection/list/$', rest_views.get_connections_list),
    url(r'people/list/$', rest_views.get_people_list),
    url(r'connection/common-list/$', rest_views.get_connections_list_in_common_param),
    url(r'^connection/(?P<username>[-\w\d]+)/$', rest_views.UserFollowerView.as_view(),),
    url(r'^status/feed/$', rest_views.get_status_feed),
    url(r'^notification/feed/$', rest_views.get_notification_feed),
    url(r'^last-opened/$', rest_views.set_last_opened)
]