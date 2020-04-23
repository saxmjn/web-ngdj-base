import jwt
from datetime import datetime
from calendar import timegm
# DJANGO
from django.contrib.auth.models import User
from rest_framework_jwt.settings import api_settings
from rest_framework import authentication, exceptions, permissions
from rest_framework_jwt.compat import get_username, get_username_field
# PROJECT
from app.utils import raise_error


def jwt_payload_handler(user):
    """
    Used to generate the payload for the JWTs issued
    :param user:
    :type user: django.contrib.auth.models.User
    :return:
    :rtype: Union[Dict[str, unicode], Dict[str, str]]
    """
    username_field = get_username_field()
    username = get_username(user)
    # 'user_id': user.pk, 'email': user.email,
    payload = { 'username': username,
                'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA, username_field: username}

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    return payload


def jwt_encode_handler(payload):
    """

    :param payload:
    :type payload: Union[Dict[str, unicode], Dict[str, str], Dict[str, str], Dict[str, unicode], Dict[str, unicode], Dict[str, unicode], Dict[str, unicode]]
    :return:
    :rtype: unicode
    """
    return jwt.encode(
        payload,
        api_settings.JWT_SECRET_KEY,
        api_settings.JWT_ALGORITHM
    ).decode('utf-8')


def jwt_decode_handler(token):
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }

    return jwt.decode(
        token,
        api_settings.JWT_SECRET_KEY,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM]
    )


def get_user_from_token(token):
    payload = jwt_decode_handler(token)
    username = payload.get('username')
    try:
        user = (User.objects.get_by_natural_key(username))
        return user
    except User.DoesNotExist:
        raise raise_error("ERR-USER-009")


def get_token_for_user(user):
    """
     Utility to function to obtain a token for a user object, creates one if it does not exist
    :type user: django.contrib.auth.models.User
    :return: The JWT
    :rtype: unicode
    """
    payload = jwt_payload_handler(user)
    value = jwt_encode_handler(payload)
    return value


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


class CSRFExemptSessionAuthentication(authentication.SessionAuthentication):
    """
    (Django)Session based Auth for DRF views/rest_views
    """

    def enforce_csrf(self, request):
        return