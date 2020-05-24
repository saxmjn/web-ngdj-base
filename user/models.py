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
from app import datetime as app_datetime
from app.utils import raise_error, validate_email, validate_get_phone, to_bool, \
    validate_phone, get_datetime
from general import firebase
from general.firebase import notify_general_to_user, setup_user_on_firebase
from general.models import Category, Phone, City, Email
from general.utils import msg91_phone_otp_verification

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "authe.User")


class UserTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=15, unique=True)
    type = models.CharField(max_length=250, choices=constants.user_tag_type_choices, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    @classmethod
    def get_from_code(cls, code):
        try:
            obj = cls.objects.get(code=code)
        except ObjectDoesNotExist:
            raise_error(code='ERR-USER-001')
        return obj

    @classmethod
    def get_tags(cls):
        return cls.objects.all()


class UserProfile(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    inviter = models.ForeignKey(AUTH_USER_MODEL, null=True, blank=True, related_name='user_inviter', on_delete=models.CASCADE)
    birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=100, choices=constants.sex_choices, null=True, blank=True)
    language = models.CharField(max_length=100, choices=constants.language_choices, null=True, blank=True)
    profile_pic_url = models.TextField(default=None, null=True, blank=True)
    heading = models.CharField(max_length=50, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, null=True, blank=True)
    signup_stage = models.PositiveIntegerField(default=0)
    signup_done = models.BooleanField(default=0)
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
    def get_users_for_categories(category_ids, offset=None):
        limit = 10
        if len(category_ids):
            query = UserProfile.objects.filter(category__in=category_ids, authorised=True)
        else:
            query = UserProfile.objects.filter(authorised=True)

        if offset is not None:
            users = query[offset: offset + limit]
        else:
            users = query

        data = {'users': users, 'count': users.count()}
        return data

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
            raise_error('ERR-DJNG-003')
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def match_user_from_email(email):
        if not validate_email(email):
            raise_error('ERR-GNRL-002')

        try:
            query = User.objects.get(email__iexact=email).userprofile
            return query
        except User.MultipleObjectsReturned:
            raise_error('ERR-DJNG-003')
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_user_from_phone_number(phone_number, phone_code):
        try:
            query = UserProfile.objects.filter(phone_number=phone_number, phone_code=phone_code)
            return query.first()
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def match_user_from_phone(phone):
        if not validate_phone(phone):
            raise_error('ERR-GNRL-002')

        phone_obj = Phone.create(phone)

        try:
            query = UserProfile.objects.get(phone_number=phone_obj.number,
                                            phone_code=phone_obj.code)
            return query
        except User.MultipleObjectsReturned:
            raise_error('ERR-DJNG-003')
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
        if operation == 'VERIFY_USER_PHONE':
            user_profile = UserProfile.match_user_from_phone(phone)

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

            user_profile = UserProfile.match_user_from_phone(phone)
            if user_profile:
                data = {'user_registered': True, 'user_profile': user_profile}
            else:
                data = {'user_registered': False, 'user_profile': user_profile}

        elif operation == 'SEND_PHONE_VERIFICATION_OTP':

            user_profile = UserProfile.match_user_from_phone(phone)
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
            user_profile = UserProfile.match_user_from_phone(phone)

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
    def create(cls, email, first_name, last_name, username=None, phone=None):
        if phone and UserProfile.match_user_from_phone(phone):
            raise_error('ERR-USER-004')
        if UserProfile.match_user_from_email(email=email):
            raise_error('ERR-USER-005')
        if username and UserProfile.match_user_from_username(username):
            raise_error('ERR-USER-008')

        if username is None:
            username = UserProfile.get_random_username(first_name)

        user = User.objects.create(username=username, email=email, first_name=first_name, last_name=last_name)
        user_profile = cls.objects.create(user=user)
        return user_profile

    @classmethod
    def create_with_phone(cls, phone_number, email, first_name, last_name, username=None, phone_otp=None):
        stored_phone = Phone.create(phone=phone_number)
        if phone_otp and (stored_phone.otp != phone_otp):
            raise_error('ERR-AUTH-005')
        user_profile = cls.create(email=email, first_name=first_name, last_name=last_name, username=username)
        user_profile.phone_number = stored_phone.number
        user_profile.phone_code = stored_phone.code
        user_profile.phone_otp = stored_phone.otp
        if phone_otp:
            user_profile.phone_verified = True
        user_profile.save()
        return user_profile

    @classmethod
    def admin_create(cls, first_name, last_name, email, profile_image, heading, category_code,
                     username=None, phone_number=None):
        if UserProfile.match_user_from_phone(phone_number) is not None:
            raise_error('ERR-USER-004')
        if UserProfile.match_user_from_email(email=email) is not None:
            raise_error('ERR-USER-005')
        try:
            user = User.objects.get(username=username)
            raise_error('ERR-USER-002')
        except User.MultipleObjectsReturned:
            raise_error('ERR-DJNG-003')
        except ObjectDoesNotExist:
            if username is None and email is not None:
                username = UserProfile.get_random_username_email(first_name)[0]
            elif username is None and email is None:
                username, email = UserProfile.get_random_username_email(first_name)
            user = User.objects.create(username=username, email=email, first_name=first_name, last_name=last_name)
            user_profile = cls.objects.create(user=user, authorised=True)

        cls.update(user=user, first_name=first_name, last_name=last_name, profile_image=profile_image, heading=heading,
                   category_code=category_code)
        return user_profile

    @classmethod
    def update_username(cls, user, username):
        if user is None or username is None:
            return
        try:
            user_obj = User.objects.get(username=username)
            if user != user_obj:
                raise_error('ERR-USER-007')
        except ObjectDoesNotExist:
            user.username = username
            user.save()

    @classmethod
    def update_email(cls, user, new_email, otp, password):
        if user is None or new_email is None or otp is None  or password is None:
            return
        
        if not validate_email(email=new_email):
            raise_error('ERR-GNRL-IVALID-EMAIL')
        
        stored_otp = Email.get_otp(email=new_email)
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
        stored_phone = Phone.create(phone=phone)
        if not OTP:
            raise_error('ERR-AUTH-005')
        if stored_phone.otp != OTP:
            raise_error('ERR-AUTH-005')

        user_profile = UserProfile.match_user_from_phone(phone)
        phone_data = validate_get_phone(phone)
        if user_profile is not None and user_profile != self:
            raise_error('ERR-USER-007')
        else:
            self.phone_code = phone_data['phone_code']
            self.phone_number = phone_data['phone_number']
            self.phone_otp = OTP
            self.save()

        return {'message': 'Phone updated successfully'}

    def update_category(self, category_code):
        if category_code is None:
            return
        try:
            category = Category.objects.get(code=category_code)
        except ObjectDoesNotExist:
            raise ValueError('No category found')

        self.category = category
        self.save()

    def update_categories(self, categories_list):
        if categories_list is None:
            return
        categories = Category.objects.filter(code__in=categories_list)
        existing = self.categories.all()
        for e in existing:
            self.categories.remove(e)
            self.save()

        self.categories.add(*categories)

        for c in categories:
            self.categories.add(c)
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
    def update(cls, user, first_name=None, last_name=None, username=None, email=None, profile_image=None,
               heading=None, summary=None, sex=None, city_code=None, location=None,
               birth=None, category_code=None, category_code_list=None, device_token=None):
        
        obj = cls.get_from_user(user=user)
        cls.update_username(user=user, username=username)
        obj.update_category(category_code=category_code)
        obj.update_categories(categories_list=category_code_list)
        obj.update_city(city_code=city_code)

        if first_name:
            obj.user.first_name = first_name
        if last_name:
            obj.user.last_name = last_name
        if profile_image:
            obj.profile_pic_url = profile_image
        if heading:
            obj.heading = heading
        if summary:
            obj.summary = summary
        if location:
            obj.location = location
        if birth:
            obj.birth = get_datetime(birth)
        if sex:
            obj.sex = sex
        if device_token is not None:
            obj.device_token = device_token
        obj.modified = app_datetime.now
        obj.user.save()
        obj.save()
        return obj

    def update_datetime(self, operation, datetime):
        if operation == 'NEW_BROADCAST':
            self.last_broadcasted_at = datetime
            self.save()

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
            UserProfile.objects.filter(city=self.city, category=self.category).values_list('user', flat=True))
        following_pks = list(
            UserFollower.objects.filter(follower=self.user, active=True).values_list('user', flat=True))

        suggestion_pks = list(
            set(contact_pks + list(set(random_pks) - set(contact_pks))) - set(following_pks) - set([self.user.id]))

        suggestions = User.objects.filter(pk__in=suggestion_pks)

        data = {'suggestions': suggestions}
        return data


class UserFollower(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    follower = models.ForeignKey(AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = (('user', 'follower'),)

    def is_user_expert(self):
        return self.user.userprofile.is_expert()

    def toggle_subscription_from_firebase(self):
        topic = 'user-' + str(self.user.pk)
        if self.active is True:
            firebase.subscribe_to_topic(topic=topic, user=self.follower)
        elif self.active is False:
            firebase.unsubscribe_from_topic(topic=topic, user=self.follower)

    @classmethod
    def create(cls, followee, follower):
        # If folowee and follower are same
        if followee == follower:
            raise ValueError('You cannot follow yourself')
        obj, status = cls.objects.get_or_create(user=followee, follower=follower)
        return obj

    @classmethod
    def update(cls, followee, follower):
        obj = cls.create(followee, follower)
        if obj.active is False or obj.active is None:
            obj.active = True
            obj.save()
        elif obj.active is True:
            obj.active = False
            obj.save()
        data = {'is_followed': obj.active}

        print(data)

        obj.toggle_subscription_from_firebase()
        return data

    @classmethod
    def delete(cls, followee, follower):
        try:
            obj = cls.objects.get(user=followee, follower=follower)
            obj.delete()
        except:
            raise ValueError('No such relation found')

    @classmethod
    def find_followers_pks(cls, user):
        follower_pks = cls.objects.filter(user=user, active=True).values_list('follower', flat=True)
        return follower_pks

    @classmethod
    def find_followers(cls, user):
        follower_pks = cls.objects.filter(user=user, active=True).values_list('follower', flat=True)
        followers = User.objects.filter(pk__in=follower_pks)
        data = {'connections': followers, 'count': len(follower_pks)}
        return data

    @classmethod
    def get_followers_count(cls, user):
        count = cls.objects.filter(user=user, active=True).count()
        return count

    @classmethod
    def find_followings(cls, user):
        following_pks = cls.objects.filter(follower=user, active=True).values_list('user', flat=True)
        followings = User.objects.filter(pk__in=following_pks)
        data = {'connections': followings, 'count': len(following_pks)}
        return data

    @staticmethod
    def get_connections(user, operation):
        if operation == 'FIND_FOLLOWERS':
            return UserFollower.find_followers(user=user)
        elif operation == 'FIND_FOLLOWINGS':
            return UserFollower.find_followings(user=user)

    @staticmethod
    def get_people(user, code, type):
        if type == 'CITY':
            people_pks = list(
                UserProfile.objects.filter(city__code=code).values_list('user', flat=True))
        elif type == 'INTEREST':
            people_pks = list(
                UserProfile.objects.filter(categories__code=code).values_list('user', flat=True))
        else:
            raise_error('')

        following_pks = list(UserFollower.objects.filter(follower=user, active=True).values_list('user', flat=True))
        follower_pks = list(UserFollower.objects.filter(user=user, active=True).values_list('follower', flat=True))

        all_pks = list(set(list(set(following_pks).intersection(set(people_pks))) + list(
            (set(follower_pks) - set(following_pks)).intersection(people_pks)) + list(
            set(people_pks) - set(follower_pks) - set(following_pks))) - set([user.id]))

        print('people_pks', people_pks)
        print('following_pks', following_pks)
        print('follower_pks', follower_pks)
        print('all_pks', all_pks)

        all = User.objects.filter(pk__in=all_pks)
        data = {'all': all}
        return data

    @staticmethod
    def get_connections_with_common(user, parameter):
        if parameter == 'CITY':
            people_pks = list(
                UserProfile.objects.filter(city__code=user.userprofile.city.code).values_list('user', flat=True))
        elif parameter == 'INTEREST':
            people_pks = list(
                UserProfile.objects.filter(category__code=user.userprofile.category.code).values_list('user',
                                                                                                      flat=True))
        else:
            raise_error('')

        following_pks = list(UserFollower.objects.filter(follower=user, active=True).values_list('user', flat=True))
        follower_pks = list(UserFollower.objects.filter(user=user, active=True).values_list('follower', flat=True))

        all_pks = list(set(list(set(following_pks).intersection(set(people_pks))) + list(
            (set(follower_pks) - set(following_pks)).intersection(people_pks)) + list(
            set(people_pks) - set(follower_pks) - set(following_pks))) - set([user.id]))

        print('people_pks', people_pks)
        print('following_pks', following_pks)
        print('follower_pks', follower_pks)
        print('all_pks', all_pks)

        all = User.objects.filter(pk__in=all_pks)

        data = {'all': all}
        return data

    @classmethod
    def find_followings_and_status_updates(cls, user):
        following_pks = cls.objects.filter(follower=user, active=True).values_list('user', flat=True)
        followings = UserProfile.objects.filter(user_id__in=following_pks,
                                                status_updated_at__gte=app_datetime.today,
                                                status_updated_at__lt=app_datetime.tomorrow).exclude(
            Q(status__isnull=True) | Q(status__exact='')).order_by('-status_updated_at')
        data = {'followings': followings, 'count': followings.count()}
        return data

    @classmethod
    def get_following_count(cls, user):
        count = cls.objects.filter(follower=user, active=True).count()
        return count

    @classmethod
    def check_if_follow(cls, followee, follower):
        try:
            obj = cls.objects.get(user=followee, follower=follower)
            return obj.active
        except ObjectDoesNotExist:
            return None

    @classmethod
    def follow_users(cls, followees, follower):
        for followee in followees:
            cls.update(followee, follower, True)


class UserGoogleData(models.Model):
    """
        Helps store the Data taken from Google for a User
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uid = models.TextField(unique=True)
    image_url = models.TextField(blank=True, null=True,
                                 help_text="The image_url given by google")
    id_token = models.TextField(blank=True, null=True,
                                help_text="The id token given by google, this will expire in a short duration")
    data = models.TextField(blank=True, help_text="The raw  API response coming in from about containing "
                                                  "information about the User")

    class Meta:
        get_latest_by = "created"
        ordering = ['-created']
        verbose_name_plural = "User Google Data"
        verbose_name = "User Google Data"

    @staticmethod
    def create(user, data):
        try:
            data['id']
        except KeyError:
            raise ValueError()

        if data['email'] != user.email:
            raise ValueError()

        obj = UserGoogleData.objects.create(user_profile=user.userprofile, uid=data['id'],
                                            image_url=data['image_url'], id_token=data['id_token'],
                                            data=json.dumps(data))
        return obj

    def update(self, extra_data):
        self.id_token = extra_data['id_token']
        self.image_url = extra_data['image_url']
        self.data = json.dumps(extra_data)
        self.save()


class UserFacebookData(models.Model):
    """
    Helps store the Data taken from Facebook for a User
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    uid = models.TextField(help_text="The unique ID of the Facebook Profile of the User")
    data = models.TextField(blank=True, help_text="The raw  API response coming in from about containing "
                                                  "information about the User")
    token = models.TextField(help_text="The access token given by Facebook, this will expire in a short duration")

    class Meta:
        get_latest_by = "created"
        ordering = ['-created']
        verbose_name_plural = "User Facebook Data"
        verbose_name = "User Facebook Data"


class UserLinkedInData(models.Model):
    """
    Helps store the Data taken from LinkedIn for a User
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    uid = models.TextField(help_text="The unique ID of the LinkedIn Profile of the User")
    data = models.TextField(null=True, blank=True, help_text="The raw  API response coming in from about containing "
                                                             "information about the User")
    token = models.TextField(null=True,
                             help_text="The access token given by LinkedIn, this will expire in a short duration")

    class Meta:
        get_latest_by = "created"
        ordering = ['-created']
        verbose_name_plural = "User LinkedIn Data"
        verbose_name = "User LinkedIn Data"

    @classmethod
    def update(cls, uid, user, data=None, token=None):
        try:
            obj = cls.objects.get(uid=uid)
            if obj.user != user:
                raise_error(code='ERR0003')
            else:
                obj.token = token
                obj.data = data
                obj.save()
        except ObjectDoesNotExist:
            obj = cls.objects.create(uid=uid, user=user, token=token, data=data)

        return obj


class UserNotification(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    sender = models.ForeignKey(AUTH_USER_MODEL, related_name="notification_sender", on_delete=models.CASCADE)
    type = models.CharField(choices=constants.notification_type_states_choices, max_length=500, null=True,
                            blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    reference_id = models.CharField(max_length=500, null=True, blank=True)
    reference_type = models.CharField(choices=constants.reference_type_states_choices, max_length=500, null=True,
                                      blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    @staticmethod
    def new_follower(connection):
        if connection.active:
            user = connection.user
            sender = connection.follower
            type = 'NEW_FOLLOWER'
            title = '{} has started following you'.format(sender.first_name)
            UserNotification.objects.create(user=user, sender=sender, type=type, title=title)
            total_count = UserNotification.objects.filter(user=user).count()
            notify_general_to_user(to_user=user, count=total_count)
            firebase.push_notification_trigger(to_user=user, from_user=sender, type='NEW_FOLLOWER', reference_id=sender.id, reference_username=sender.username)

    @staticmethod
    def get_notifications(user, offset=0):
        limit = 10
        offset = int(offset)
        total_count = UserNotification.objects.filter(user=user).count()
        if offset == 0:
            user.userprofile.read_notification_count = total_count
            user.userprofile.save()
        notifications = UserNotification.objects.filter(user=user).order_by('-created')[offset:offset + limit]
        read_count = user.userprofile.read_notification_count
        data = {'notifications': notifications, 'total_count': total_count, 'read_count': read_count}
        return data
