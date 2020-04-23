from django.conf.urls import url
from . import rest_views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token


urlpatterns = [
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^email-auth/', rest_views.EmailAuth.as_view()),
    url(r'^phone-auth/', rest_views.PhoneAuth.as_view()),
    url(r'^google-auth/', rest_views.GoogleAuth.as_view()),
    url(r'^linkedin-auth/', rest_views.LinkedinAuth.as_view()),
    url(r'^linkedin-auth-mobile/', rest_views.linkedin_auth_mobile),
    url(r'^registration/', rest_views.registration),
    url(r'^password-set/', rest_views.set_password),
    url(r'^password-reset/', rest_views.reset_password)
]