from __future__ import unicode_literals
import uuid
# DJANGO
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from commune.utils import raise_error
from commune import settings, constants
from . import utils
# PROJECT

from commune.fields import UUIDField
from commune.utils import validate_get_phone, random_with_N_digits, validate_email


class File(models.Model):
    """
    Used to store files on S3 at the moment
    Based on the architecture suggested at https://devcenter.heroku.com/articles/s3-upload-python
    Helps to generate secure URLs to upload/obtain files
    """
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    type = models.CharField(max_length=250, help_text="The MIME type of the file")
    url = models.TextField(null=True, blank=True)
    bucket = models.CharField(max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.file_name

    @classmethod
    def get_obj(cls, unique_id):
        try:
            obj = cls.objects.get(uuid=unique_id)
        except ObjectDoesNotExist:
            raise ValueError('No File found')
        return obj

    @staticmethod
    def store_public_file(bucket, file_name):
        file = File.objects.create()
        file.name = file_name
        file.bucket = bucket
        file.save()
        if bucket == 'event':
            S3_BUCKET = 'cmn-event-thumbnail'
        elif bucket == 'story':
            S3_BUCKET = 'cmn-story-thumbnail'
        else:
            file.delete()
            raise ValueError('No bucket found')
        access_control = 'public-read';
        AWSAccessKeyId = 'AKIAJVMG2OZHAAZP44AA';
        AWSSecretKey = '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';
        url = 'https://%s.s3.amazonaws.com/%s?AWSAccessKeyId=%s' % (S3_BUCKET, file.uuid, AWSAccessKeyId)

        file.set_url()
        data = {
            'access_control': access_control,
            'signed_request': url,
            'name': file.name,
            'uuid': file.uuid,
            'url': file.url
        }
        return data

    def set_url(self):
        url = 'https://s3.ap-south-1.amazonaws.com/%s/%s'
        if self.bucket == 'product-image':
            url = url % ('cmn-product-image', self.uuid)
        if self.bucket == 'product-thumbnail':
            url = url % ('cmn-product-thumbnail', self.uuid)
        elif self.bucket == 'business-logo':
            url = url % ('cmn-brand-logo', self.uuid)
        else:
            return None

        self.url = url
        self.save()

    @staticmethod
    def get_url(bucket, uuid):
        url = 'https://s3.ap-south-1.amazonaws.com/%s/%s'
        if bucket == 'product-image':
            url = url % ('cmn-product-image', uuid)
        if bucket == 'product-thumbnail':
            url = url % ('cmn-product-thumbnail', uuid)
        elif bucket == 'business-logo':
            url = url % ('cmn-brand-logo', uuid)
        else:
            return None
        return url


class Email(models.Model):
    email = models.CharField(max_length=250, unique=True)
    otp = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    @staticmethod
    def create(email, send_otp=False):
        if not  validate_email(email):
            raise_error('ERR-GNRL-INVALID-EMAIL')
        try:
            obj = Email.objects.get(email=email)
        except ObjectDoesNotExist:
            obj = Email.objects.create(email=email, otp=random_with_N_digits(6))
        if send_otp and settings.ENV_SETUP == 'PRODUCTION':
            pass
        return obj

    @staticmethod
    def get_email(email):
        try:
            obj = Email.objects.get(email=email)
        except ObjectDoesNotExist:
            raise_error('ERR-DJNG-002')
        return obj


class Phone(models.Model):
    number = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    otp = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        unique_together = (('number', 'code'),)

    @staticmethod
    def create(phone, send_otp=False):
        phone_data = validate_get_phone(phone)
        try:
            obj = Phone.objects.get(number=phone_data['phone_number'], code=phone_data['phone_code'])
            obj.otp = random_with_N_digits(6)
            obj.save()
        except ObjectDoesNotExist:

            obj = Phone.objects.create(number=phone_data['phone_number'],
                                   code=phone_data['phone_code'], otp=random_with_N_digits(6))
        if send_otp and settings.ENV_SETUP == 'PRODUCTION':
            utils.msg91_phone_otp_verification(phone=obj.number, OTP=obj.otp)
        return obj

    @staticmethod
    def get_phone(phone_number, phone_code):
        try:
            obj = Phone.objects.get(number=phone_number, code=phone_code)
            return obj
        except ObjectDoesNotExist:
            raise_error('ERR-DJNG-002')


    @staticmethod
    def get_otp(phone_number, phone_code):
        try:
            obj = Phone.objects.get(number=phone_number, code=phone_code)
            return obj.otp
        except ObjectDoesNotExist:
            raise_error('ERR-DJNG-002')


class Tag(models.Model):
    code = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    parent = models.CharField(max_length=100, choices=constants.tag_parent_choices, null=True, blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)


class Category(models.Model):
    code = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.name + ' (' + self.code + ')'

    @classmethod
    def get_categories(cls):
        categories = cls.objects.all().order_by('name')
        data = {'categories': categories, 'count': categories.count()}
        return data


class City(models.Model):
    code = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    def __str__(self):
        return self.name + ' (' + self.code + ')'

    @classmethod
    def get_cities(cls):
        cities = cls.objects.all().order_by('name')
        data = {'cities': cities, 'count': cities.count()}
        return data

    email = models.EmailField(max_length=500)
    subscribed = models.NullBooleanField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.email

    @classmethod
    def create(cls, email):
        valid_email = email.lower()
        try:
            obj = cls.objects.get(email=valid_email)
        except ObjectDoesNotExist:
            obj = cls.objects.create(email=valid_email)
        return obj