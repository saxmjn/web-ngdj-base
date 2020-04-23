from django.conf.urls import url, include

urlpatterns = [
    url(r'^authe/', include('authe.api_urls')),
    url(r'^general/', include('general.api_urls')),
    url(r'^user/', include('user.api_urls')),
]