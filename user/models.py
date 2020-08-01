from __future__ import unicode_literals

import json
import uuid

# DJANGO
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

# PROJECT
from app import constants
from app import _datetime as datetime
from app import _firebase as firebase
from app.utils import (raise_error, validate_email, validate_get_phone, to_bool, validate_phone)
from general.models import Phone, City, Email
from general.utils import msg91_phone_otp_verification

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "authe.User")


class UserProfile(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    inviter = models.ForeignKey(AUTH_USER_MODEL, null=True, blank=True, related_name='user_inviter', on_delete=models.CASCADE)
    birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=100, choices=constants.sex_choices, null=True, blank=True)
    language = models.CharField(max_length=100, choices=constants.language_choices, null=True, blank=True)
    image = models.TextField(default=None, null=True, blank=True)
    image_modified_at = models.DateTimeField(null=True, blank=True, editable=True)
    heading = models.CharField(max_length=50, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, null=True, blank=True)
    signup_stage = models.PositiveIntegerField(default=0)
    signup_done = models.BooleanField(default=0)
    email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=250, null=True, blank=True)
    phone_code = models.CharField(max_length=250, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    authorised = models.NullBooleanField(blank=True)
    read_notification_count = models.PositiveIntegerField(default=0)
    device_token = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    last_opened_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        verbose_name = "User Profile"

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' (' + self.user.username + ')'

    @classmethod
    def get_users(cls, offset=None):
        limit = 10
        query = cls.objects.filter(authorised=True)
        if offset is not None:
            objs = query[offset: offset + limit]
        else:
            objs = query
        return objs

    @staticmethod
    def get_users_suggestion():
        users = UserProfile.objects.filter(editor_pick=True, authorised=True)

        data = {'users': users, 'count': users.count()}
        return data

    @classmethod
    def get_from_user(cls, user):
        try:
            obj = cls.objects.get(user=user)
        except ObjectDoesNotExist:
            raise_error(code='ERR-USER-001')
        return obj

    @classmethod
    def get_from_username(cls, username):
        try:
            obj = cls.objects.get(user__username=username)
        except ObjectDoesNotExist:
            raise_error(code='ERR-USER-001')
        return obj

    def get_username(self):
        return self.user.username

    def get_email(self):
        return self.user.email

    def get_email_if_allowed(self):
        if self.permission_email_public:
            return self.get_email()
        else:
            return None

    def get_phone_number(self):
        return self.phone_number

    def get_phone_code(self):
        return self.phone_code

    def get_phone(self):
        phone = ''
        if self.phone_code and self.phone_number:
            phone = '+' + self.phone_code + self.phone_number

        return phone

    def get_phone_if_allowed(self):
        if self.permission_phone_public:
            return self.get_phone()
        else:
            return None

    def get_first_name(self):
        return self.user.first_name

    def get_last_name(self):
        return self.user.last_name

    def get_name(self):
        name = ''
        first_name = self.get_first_name()
        last_name = self.get_last_name()
        if first_name:
            name = name + first_name
        if last_name:
            name = name + ' ' + last_name
        return name

    def get_authorised(self):
        return self.authorised

    def get_sex(self):
        return self.sex

    def get_heading(self):
        return self.heading

    def get_summary(self):
        return self.summary

    def get_status(self):
        return self.status

    def get_profile_image(self):
        # return self.profile_pic_url
        image = 'link-to-your-s3-bucket/{}.png'.format(self.user.username)
        return image

    def get_inviter(self):
        return self.inviter

    def set_phone_otp(self):
        if not self.phone_otp:
            phone_date = Phone.create(self.phone_number)
            self.phone_otp = phone_date.otp
            self.save()

    def set_last_opened(self):
        import datetime
        self.last_opened_at = datetime.datetime.now()
        self.save()


    @staticmethod
    def get_random_username(first_name):
        first_name = first_name.replace(' ', '')
        uid = str(uuid.uuid4())[0:6]
        username = (first_name + uid).lower()
        try:
            User.objects.get(username=username)
            return UserProfile.get_random_username(first_name)
        except ObjectDoesNotExist:
            return username

    @staticmethod
    def get_random_username_email(first_name):
        uid = str(uuid.uuid4())[0:6]
        username = (first_name + uid).lower()
        try:
            User.objects.get(username=username)
            return UserProfile.get_random_username(first_name)
        except ObjectDoesNotExist:
            email = username + '@random.xyz'
        return username, email

    @staticmethod
    def match_user_from_username(username):
        try:
            query = UserProfile.objects.get(username__iexact=username)
            return query
        except User.MultipleObjectsReturned:
            raise_error('ERR-MULTIPLE-OBJECTS')
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def match_user_from_email(email):
        try:
            query = User.objects.get(email__iexact=email).userprofile
            return query
        except User.MultipleObjectsReturned:
            raise_error('ERR-MULTIPLE-OBJECTS')
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def match_user_from_phone(phone_number, phone_code):
        try:
            query = UserProfile.objects.get(phone_number=phone_number,
                                            phone_code=phone_code)
            return query
        except User.MultipleObjectsReturned:
            raise_error('ERR-MULTIPLE-OBJECTS')
        except ObjectDoesNotExist:
            return None

    def verify_phone(self, OTP):
        self.set_phone_otp()

        if self.phone_otp == OTP:
            self.phone_verified = True
            self.save()
            verified = True
        else:
            raise_error('ERR0011')
            verified = False
        data = {'phone_verified': verified}
        return data

    @staticmethod
    def phone_input(operation, phone, OTP=None):
        if not validate_phone(phone):
            raise_error('ERR-GNRL-INVALID-PHONE')

        phone_obj = Phone.create(phone)

        if operation == 'VERIFY_USER_PHONE':
            user_profile = UserProfile.match_user_from_phone(phone_obj.phone_number, phone_obj.phone_code)

            if not user_profile:
                raise_error('ERR-USER-001')
            if not OTP:
                raise_error('')
            if not user_profile.phone_otp:
                raise_error('ERR-USER-006')
            if not (user_profile.phone_otp == OTP):
                raise_error('ERR-AUTH-005')

            user_profile.phone_verified = True
            user_profile.save()
            verified = True
            data = {'phone_verified': verified}
            return data

        elif operation == 'VERIFY_USER_REGISTRATION':

            user_profile = UserProfile.match_user_from_phone(phone_obj.phone_number, phone_obj.phone_code)
            if user_profile:
                data = {'user_registered': True, 'user_profile': user_profile}
            else:
                data = {'user_registered': False, 'user_profile': user_profile}

        elif operation == 'SEND_PHONE_VERIFICATION_OTP':
            user_profile = UserProfile.match_user_from_phone(phone_obj.phone_number, phone_obj.phone_code)
            if user_profile:
                user_profile.set_phone_otp()
                msg91_phone_otp_verification(phone=phone, OTP=user_profile.phone_otp)
                data = {'message': 'OTP Sent'}
            else:
                raise_error('ERR-USER-001')

        elif operation == 'SEND_PHONE_VERIFICATION_OTP_ALLOW_ANY':
            Phone.create(phone=phone, send_otp=True)
            return {'message': 'OTP Sent'}

        elif operation == 'VERIFY_USER_REGISTRATION_SEND_OTP':
            user_profile = UserProfile.match_user_from_phone(phone_obj.phone_number, phone_obj.phone_code)

            if user_profile:
                user_profile.set_phone_otp()
                # msg91_phone_otp_verification(phone=phone, OTP=user_profile.phone_otp)
            else:
                phone_obj = Phone.create(phone)
                # msg91_phone_otp_verification(phone=phone, OTP=phone_obj.otp)

            if user_profile:
                data = {'user_registered': True}
            else:
                data = {'user_registered': False}

        return data

    @classmethod
    def create(cls, first_name, last_name, username=None, email=None, phone=None, email_otp=None, phone_otp=None):
        email_verified = False
        phone_verified = False
        phone_data = None
        if not email and not phone:
            raise_error('ERR-AUTH-DETAIL-MISSING')
        if email:
            if not validate_email(email):
                raise_error('ERR-GNRL-INVALID-EMAIL')
            if email_otp and (Email.get_email(email=email).otp != email_otp):
                raise_error('ERR-AUTH-INVALID-OTP')
            else:
                email_verified = True
            if UserProfile.match_user_from_email(email=email):
                raise_error('ERR-USER-OTHER-WITH-EMAIL')
        if phone:
            if not email:
                email = UserProfile.get_random_username_email(first_name=first_name)[1]
            phone_data = validate_get_phone(phone)
            if phone_otp and (Phone.get_phone(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code']).otp != phone_otp):
                raise_error('ERR-AUTH-INVALID-OTP')
            else:
                phone_verified = True
            if UserProfile.match_user_from_phone(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code']):
                raise_error('ERR-USER-OTHER-WITH-PHONE')
        if username and UserProfile.match_user_from_username(username):
            raise_error('ERR-USER-OTHER-WITH-USERNAME')

         if username is None or not username:
            username = UserProfile.get_random_username(first_name)

        user = User.objects.create(username=username, email=email, first_name=first_name, last_name=last_name)
        user_profile = cls.objects.create(user=user)
        if email_verified:
            user_profile.email_verified = True
        if phone_data:
            user_profile.phone_number = phone_data['phone_number']
            user_profile.phone_code = phone_data['phone_code']
        if phone_verified:
            user_profile.phone_otp = phone_otp
            user_profile.phone_verified = True
        user_profile.save()
        return user_profile

    @classmethod
    def create_from_email(cls, email, first_name, last_name, phone=None, username=None, otp=None):
        if not email:
            raise_error('ERR-GNRL-IVALID-EMAIL')
        user_profile = cls.create(email=email, first_name=first_name, last_name=last_name, username=username, phone=phone, email_otp=otp)
        return user_profile

    @classmethod
    def create_with_phone(cls, phone, first_name, last_name, username=None, otp=None, email=None,):
        if not phone:
            raise_error('ERR-GNRL-INVALID-PHONE')
        user_profile = cls.create(phone=phone, email=email, first_name=first_name, last_name=last_name, username=username, phone_otp=otp)
        return user_profile

    @classmethod
    def admin_create(cls, first_name, last_name, profile_image, heading, email=None,
                     username=None, phone=None):
        user_profile = cls.create(phone=phone, email=email, first_name=first_name, last_name=last_name, username=username)
        return user_profile

    @classmethod
    def update_username(cls, user, username):
        if user is None or username is None:
            return
        try:
            user_obj = User.objects.get(username=username)
            if user != user_obj:
                raise_error('ERR-USER-OTHER-WITH-USERNAME')
        except ObjectDoesNotExist:
            user.username = username
            user.save()

    @classmethod
    def update_email(cls, user, new_email, otp, password):
        if user is None or new_email is None or otp is None  or password is None:
            return
        
        if not validate_email(email=new_email):
            raise_error('ERR-GNRL-IVALID-EMAIL')
        
        stored_otp = Email.get_email(email=new_email).otp
        if stored_otp != otp:
            raise_error('ERR-AUTH-INVALID-OTP')
        
        if not user.check_password(password):
            raise_error('ERR-AUTH-INVALID-PASSWORD')
        try:
            user_obj = User.objects.get(email=new_email)
            if user != user_obj:
                raise_error('ERR-USER-OTHER-WITH-EMAIL')
            else:
                raise_error('ERR-USER-YOU-WITH-EMAIL')
        except ObjectDoesNotExist:
           user.email = new_email
           user.save()


    def update_phone(self, phone, OTP):
        phone_data = validate_get_phone(phone)
        if not OTP:
            raise_error('ERR-AUTH-005')
        if OTP and (Phone.get_phone(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code']).otp != OTP):
                raise_error('ERR-AUTH-INVALID-OTP')

        user_profile = UserProfile.match_user_from_phone(phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code'])
        if user_profile is not None and user_profile != self:
            raise_error('ERR-USER-OTHER-WITH-PHONE')
        else:
            self.phone_code = phone_data['phone_code']
            self.phone_number = phone_data['phone_number']
            self.phone_otp = OTP
            self.phone_verified = True
            self.save()

    def update_city(self, city_code):
        if city_code is None:
            return
        try:
            city = City.objects.get(code=city_code)
        except ObjectDoesNotExist:
            raise ValueError('No city found')

        self.city = city
        self.save()

    @classmethod
    def update(cls, user, first_name=None, last_name=None, username=None, email=None, image=None, image_modified=False, heading=None, summary=None, sex=None, city_code=None, location=None, birth=None, device_token=None, last_opened_at=None):
        
        obj = cls.get_from_user(user=user)
        cls.update_username(user=user, username=username)

    def store_data(self, first_name=None, last_name=None, username=None, email=None, image=None, image_modified=False, heading=None, summary=None, sex=None, city_code=None, location=None, birth=None, device_token=None, last_opened_at=None):
        self.update_city(city_code=city_code)

        if first_name:
            self.user.first_name = first_name
        if last_name:
            self.user.last_name = last_name
        if image:
            self.image = image
        if image_modified:
            self.image_modified = datetime.current_datetime('Asia/Kolkata')
        if heading:
            self.heading = heading
        if summary:
            self.summary = summary
        if location:
            self.location = location
        if birth:
            self.birth = datetime.get_datetime(birth)
        if sex:
            self.sex = sex
        if device_token is not None:
            self.device_token = device_token
        if last_opened_at is not None:
            self.last_opened_at = last_opened_at
        self.modified = datetime.now
        self.user.save()
        self.save()
        return self

    def check_if_followed_by(self, follower):
        try:
            obj = UserFollower.objects.get(user=self.user, follower=follower)
            return obj.active
        except ObjectDoesNotExist:
            return None

    def get_suggestions(self):
        from contacts.models import UserContact
        contact_pks = list(UserContact.get_contacts_on_tc(user=self.user)['contact_pks'])
        random_pks = list(
            UserProfile.objects.filter(city=self.city).values_list('user', flat=True))
        following_pks = list(
            UserFollower.objects.filter(follower=self.user, active=True).values_list('user', flat=True))

        suggestion_pks = list(
            set(contact_pks + list(set(random_pks) - set(contact_pks))) - set(following_pks) - set([self.user.id]))

        suggestions = User.objects.filter(pk__in=suggestion_pks)

        data = {'suggestions': suggestions}
        return data
