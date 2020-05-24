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

#### Development:
##### 1. Installing Libraries
We will first start with first installing with proper jwt libraries for django and including them in app/settings.py as shown here

> Code snippet from settings.py
```
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication'
        ...
        ...
    ],
}
```

```
JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 300,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=300),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=300),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}
```
##### 2. Writing JWT Utils
There are set of functions in authe/jwt_utils.py file that are relevant here. We in this document we will restrict to explaing the purpose of class JWTAuthentication.

> Code snippet from authe/jwt_utils.py
```
class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            JWToken = request.META.get('HTTP_AUTHORIZATION')[5:].split('>')[0]
        except Exception:
            JWToken = None
        # If no token return None - no user was authenticated with the JWT
        if not JWToken:
            return None
        try:
            user = get_user_from_token(JWToken)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User Blocked')
        return user, None

    def enforce_csrf(self, request):
        return
```

##### 3. Writing APIs and defining endpoints

> Code snippet from authe/api_urls.py
```
urlpatterns = [
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^phone-auth/', rest_views.PhoneAuth.as_view()),
    url(r'^password-set/', rest_views.set_password),
    url(r'^password-reset/', rest_views.reset_password)
]
```

##### 4. Handling token on client side

So basically your response body looks something like this. After that you are going to store the access token on the client side, usually in the localStorage.
```
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQ1MjI0MjU5LCJqdGkiOiIyYmQ1NjI3MmIzYjI0YjNmOGI1MjJlNThjMzdjMTdlMSIsInVzZXJfaWQiOjF9.D92tTuVi_YcNkJtiLGHtcn6tBcxLCBxz9FKD3qzhUg8",
    "user_id": "XXXX",
    "username": "NAMEXXXXX"
}

```

In order to access the protected views on the backend (i.e., the API endpoints that require authentication), you should include the access token in the header of all requests, like this:
```
http://127.0.0.1:8000/hello/ "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQ1MjI0MjAwLCJqdGkiOiJlMGQxZDY2MjE5ODc0ZTY3OWY0NjM0ZWU2NTQ2YTIwMCIsInVzZXJfaWQiOjF9.9eHat3CvRQYnb5EdcgYFzUyMobXzxlAVh_IAgqyvzCE"
```
