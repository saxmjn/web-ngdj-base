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
from commune.utils import raise_error, validate_get_phone, validate_email
from general.models import Email, Phone
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


def create_user_from_email(email, first_name, last_name, password1, password2, otp=None, phone=None, username=None):
    if password1 != password2:
        raise_error('ERR-AUTH-UNMATCHED-PASSWORD')
    user = UserProfile.create_from_email(email=email, first_name=first_name, last_name=last_name, username=username, otp=otp).user
    user.set_password(password1)
    user.save()
    token = jwt_utils.get_token_for_user(user)
    data = {'username': user.username, 'token': token, 'user_id': user.id}
    return data

def get_user_from_email(email, password):
    if not password:
        raise_error('ERR-AUTH-INVALID-CREDENTIALS')
    
    user_profile = UserProfile.match_user_from_email(email=email)
    if user_profile is None:
        raise_error('ERR-USER-NOT-FOUND')

    user = user_profile.user
    if password and user.check_password(password):
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username}
        return data    
    else:
        raise_error('ERR-AUTH-INVALID-PASSWORD')


def create_user_from_phone(phone, first_name, last_name, password1, password2, otp=None, email=None, username=None):
    if password1 != password2:
        raise_error('ERR-AUTH-UNMATCHED-PASSWORD')
    user = UserProfile.create_with_phone(phone=phone, email=email, first_name=first_name, last_name=last_name, username=username, otp=otp).user
    user.set_password(password1)
    user.save()
    token = jwt_utils.get_token_for_user(user)
    data = {'username': user.username, 'token': token, 'user_id': user.id}
    return data


def get_user_from_phone(phone, password=None, phone_otp=None):
    if not password and not phone_otp:
        raise_error('ERR-AUTH-INVALID-CREDENTIALS')
    
    phone_data = validate_get_phone(phone)
    user_profile = UserProfile.match_user_from_phone(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code'])

    if user_profile is None:
        raise_error('ERR-USER-NOT-FOUND')

    user = user_profile.user
    if password and user.check_password(password):
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username, 'user': user}
        return data
    elif phone_otp and Phone.get_otp(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code']) == phone_otp:
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username, 'user': user}
        return data
    else:
        raise_error('ERR-AUTH-INVALID-PASSWORD')


def auth_verification(email=None, phone=None):
    username = None

    if (email is None or not email) and (phone is None or not phone):
        raise_error('ERR-AUTH-DETAIL-MISSING')

    if email and validate_email(email=email):
        userprofile = UserProfile.match_user_from_email(email=email)
        if userprofile:
            username = userprofile.user.username
    elif phone:
        phone_data = validate_get_phone(phone=phone)
        userprofile = UserProfile.match_user_from_phone(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code'])
        if userprofile:
            username = userprofile.user.username
    

    data = {'username': username}
    return data

def auth_signup(first_name, last_name, password1, password2, otp=None, email=None, phone=None, username=None, phone_otp=None, email_otp=None):
    if password1 != password2:
        raise_error('ERR-AUTH-UNMATCHED-PASSWORD')

    user = UserProfile.create(phone=phone, email=email, first_name=first_name, last_name=last_name, username=username, phone_otp=phone_otp, email_otp=email_otp).user
    user.set_password(password1)
    user.save()
    token = jwt_utils.get_token_for_user(user)
    data = {'username': user.username, 'token': token, 'user_id': user.id}
    return data

def auth_signin(password, email=None, phone=None):
    if (email is None or not email) and (phone is None or not phone):
        raise_error('ERR-AUTH-DETAIL-MISSING')
    if email:
        return get_user_from_email(email=email, password=password)
    else:
        return get_user_from_phone(phone=phone, password=password)


def reset_password(user, old_password, password1, password2):
    if not user.check_password(old_password):
            raise_error('ERR-AUTH-INVALID-PASSWORD')

    if password1 != password2:
        raise_error('ERR-AUTH-UNMATCHED-PASSWORD')

    user.set_password(password1)
    user.save()


def forgot_password(user, password1, password2, email_otp=None, phone_otp=None):
    if not password2 or not password2:
        raise_error('ERR-AUTH-DETAIL-MISSING')
    if password1 != password2:
        raise_error('ERR-AUTH-UNMATCHED-PASSWORD')
    if (email_otp is None or not email_otp) and (phone_otp is None or not phone_otp):
        raise_error('ERR-AUTH-DETAIL-MISSING')
    
    if email_otp:
        stored_email = Email.get_email(email=user.email)
        if stored_email.otp == email_otp:
            user.set_password(password1)
            user.save()
        else:
            raise_error('ERR-AUTH-INVALID-OTP')
    if phone_otp:
        stored_phone = Phone.get_phone(phone_number=user.userprofile.phone_number, phone_code=user.userprofile.phone_code)
        if stored_phone.otp == phone_otp:
            user.set_password(password1)
            user.save()
        else:
            raise_error('ERR-AUTH-INVALID-OTP')
    

def forgot_password_anonymous(password1, password2, email_otp=None, phone_otp=None, email=None, phone=None):
    if (email is None or not email) and (phone is None or not phone):
        raise_error('ERR-AUTH-DETAIL-MISSING')
    
    if email and validate_email(email=email):
        user = UserProfile.match_user_from_email(email=email).user
        forgot_password(user=user, password1=password1, password2=password2, email_otp=email_otp)
    elif phone:
        phone_data = validate_get_phone(phone=phone)
        user = UserProfile.match_user_from_phone(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code']).user
        forgot_password(user=user, password1=password1, password2=password2, phone_otp=phone_otp)

def registration(operation, phone, OTP=None, first_name=None, last_name=None, email=None, password=None):
    if operation == 'VERIFY_USER_REGISTRATION_SEND_OTP':
        data = UserProfile.phone_input(operation, phone)
        context = {'user_registered': data['user_registered']}
        return context
    elif operation == 'USER_SIGNIN':
        data = get_user_from_phone(phone=phone, phone_otp=OTP, password=password)
        return data
    elif operation == 'USER_SIGNUP':
        user = UserProfile.create_with_phone(phone=phone, otp=OTP, email=email,
                                                     first_name=first_name,
                                                     last_name=last_name).user
        if password:
            user.set_password(password)
            user.save()
        token = jwt_utils.get_token_for_user(user)
        data = {'username': user.username, 'token': token, 'user_id': user.id}
        return data