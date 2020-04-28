import json
import requests
import logging
# DJANGO
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
# PROJECT
from general.utils import msg91_phone_otp_verification
from . import jwt_utils
from commune import constants
from commune.utils import raise_error
from user.models import UserProfile, UserLinkedInData, UserGoogleData

logger = logging.getLogger("application")


def get_or_create_user_from_google(data):
    try:
        data['id']
        data['id_token']
        data['email']
    except KeyError:
        raise_error()

    try:
        google = UserGoogleData.objects.get(uid=data['id'])
        google.update(extra_data=data)
        user = google.user_profile.user
    except UserGoogleData.DoesNotExist:
        try:
            # If the user's email already exists in our DB, then just associate that user with the Google data
            user_profile = UserProfile.objects.get(user__email__iexact=data['email'])
            user = user_profile.user
        except UserProfile.DoesNotExist:
            # No data related to the user exists on our DB - so create the User, record the Data
            user = UserProfile.create(email=data['email'], first_name=data['first_name'], last_name=data['last_name']).user

        UserGoogleData.create(user=user, data=data)

    if user and user.is_active:
        token = jwt_utils.get_token_for_user(user)
        return token
    else:
        raise_error(code='ERR0006')



def get_or_create_user_from_linkedin(code, redirect_uri):
    if not code:
        raise_error(code='ERR0000')

    client_id = settings.LINKEDIN['client_id']
    client_secret = settings.LINKEDIN['client_secret']

    data = {'client_id': client_id, 'client_secret': client_secret, 'code': code, 'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(url='https://www.linkedin.com/oauth/v2/accessToken', data=data, headers=headers)
    except requests.exceptions.HTTPError as err:
        logger.error(err)
        raise_error(code='ERR0001')

    RESPONSE = json.loads(resp.text)
    print(RESPONSE)
    print(type(RESPONSE))

    try:
        access_token = RESPONSE['access_token']
    except:
        raise_error(code='ERR0002')

    file_ = requests.get(constants.linkedin_access_url, headers={"Authorization": "Bearer " + access_token})
    ret = file_.json()
    user_id_from_linkedin = ret['id']
    print(user_id_from_linkedin)
    try:
        user = UserLinkedInData.objects.get(uid=user_id_from_linkedin).user
    except ObjectDoesNotExist:
        user_email = ret['emailAddress'].encode('utf-8')
        try:
            user = User.objects.get(email=user_email)
        except ObjectDoesNotExist:
            user_first_name = ret['firstName'].encode('utf-8')
            user_last_name = ret['lastName'].encode('utf-8')
            user = UserProfile.create(email=user_email, first_name=user_first_name,last_name=user_last_name).user

        UserLinkedInData.update(uid=user_id_from_linkedin, token=access_token, data=ret, user=user)

    if user and user.is_active:
        token = jwt_utils.get_token_for_user(user)
        return token
    else:
        raise_error(code='ERR0006')


def get_or_create_user_from_linkedin_mob(user_id, email, first_name, last_name, profile_image):
    try:
        user = UserLinkedInData.objects.get(uid=user_id).user
        print(user, 1)
    except ObjectDoesNotExist:
        try:
            user = User.objects.get(email=email)
            print(user, 2)
        except ObjectDoesNotExist:
            user = UserProfile.create(email=email, first_name=first_name,last_name=last_name).user

        UserLinkedInData.update(uid=user_id, user=user)

    if user and user.is_active:
        UserProfile.update(user=user, profile_image=profile_image)
        token = jwt_utils.get_token_for_user(user)
        return token
    else:
        raise_error(code='ERR0006')


def create_user_from_email(username, email, first_name, last_name, password1, password2):
    if password1 != password2:
        raise_error('ERR-AUTH-004')

    user = UserProfile.create(email=email, first_name=first_name, last_name=last_name, username=username).user
    user.set_password(password1)
    user.save()
    return user

def get_user_from_email(email, password):
    if not password:
        raise_error('ERR-AUTH-001')
    
    user_profile = UserProfile.match_user_from_email(email=email)
    if user_profile is None:
        raise_error('ERR-USER-001')

    user = user_profile.user
    if password and user.check_password(password):
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username}
        return data    
    else:
        raise_error('ERR-AUTH-001')

def create_user_from_phone(phone_number, username, email, first_name, last_name, password1, password2):
    if password1 != password2:
        raise_error('ERR-AUTH-004')

    user = UserProfile.create_with_phone(phone_number=phone_number, email=email, first_name=first_name, last_name=last_name, username=username).user
    user.set_password(password1)
    user.save()
    token = jwt_utils.get_token_for_user(user)
    data = {'username': user.username, 'token': token, 'user_id': user.id}
    return data


def get_user_from_phone(phone_number, password=None, phone_otp=None):
    if not password and not phone_otp:
        raise_error('ERR-AUTH-001')
    user_profile = UserProfile.match_user_from_phone(phone=phone_number)

    if user_profile is None:
        raise_error('ERR-USER-001')

    user = user_profile.user
    if password and user.check_password(password):
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username}
        return data
    elif phone_otp and user_profile.phone_otp == phone_otp:
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username}
        return data
    else:
        raise_error('ERR-AUTH-001')


def registration(operation, phone, OTP=None, first_name=None, last_name=None, email=None, password=None):
    if operation == 'VERIFY_USER_REGISTRATION_SEND_OTP':
        data = UserProfile.phone_input(operation, phone)
        context = {'user_registered': data['user_registered']}
        return context
    elif operation == 'USER_SIGNIN':
        data = get_user_from_phone(phone_number=phone, phone_otp=OTP, password=password)
        return data
    elif operation == 'USER_SIGNUP':
        user = UserProfile.create_with_phone(phone_number=phone, phone_otp=OTP, email=email,
                                                     first_name=first_name,
                                                     last_name=last_name).user
        if password:
            user.set_password(password)
            user.save()
        token = jwt_utils.get_token_for_user(user)
        data = {'username': user.username, 'token': token, 'user_id': user.id}
        return data