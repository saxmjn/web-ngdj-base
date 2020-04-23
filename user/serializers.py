from django.contrib.auth.models import User
from rest_framework import serializers

# PROJECT
from app.utils import get_datetime_str
from general import serializers as general_serializer
from . import models


class UserTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserTag
        fields = ['id', 'name', 'code']


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        name = obj.first_name + ' ' + obj.last_name
        return name

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email']


class UserMiniSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    heading = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.userprofile.get_name()

    def get_heading(self, obj):
        return obj.userprofile.get_heading()

    def get_profile_image(self, obj):
        return obj.userprofile.get_profile_image()

    def get_location(self, obj):
        return None

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'name', 'heading',
                  'profile_image', 'location']


class UserMiniConnectionSerializer(UserMiniSerializer):
    is_followed = serializers.SerializerMethodField()

    def get_is_followed(self, obj):
        try:
            user = self.context['user']
            if not user.is_anonymous():
                return obj.userprofile.check_if_followed_by(follower=user)
            else:
                return False
        except KeyError:
            return False

    class Meta(UserMiniSerializer.Meta):
        model = models.User
        fields = UserMiniSerializer.Meta.fields + ['is_followed']


class UserProfileMiniSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    heading = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    def get_username(self, obj):
        username = obj.get_username()
        return username

    def get_first_name(self, obj):
        return obj.get_first_name()

    def get_last_name(self, obj):
        return obj.get_last_name()

    def get_name(self, obj):
        return obj.get_name()

    def get_heading(self, obj):
        return obj.get_heading()

    def get_profile_image(self, obj):
        return obj.get_profile_image()

    class Meta:
        model = models.UserProfile
        fields = ['id', 'username', 'first_name', 'last_name', 'name', 'heading',
                  'profile_image', 'status', 'status_updated_at']


class UserProfileBaseSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    heading = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    authorised = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    birth = serializers.SerializerMethodField()

    def get_username(self, obj):
        username = obj.get_username()
        return username

    def get_first_name(self, obj):
        return obj.get_first_name()

    def get_last_name(self, obj):
        return obj.get_last_name()

    def get_name(self, obj):
        return obj.get_name()

    def get_heading(self, obj):
        return obj.get_heading()

    def get_summary(self, obj):
        return obj.get_summary()

    def get_profile_image(self, obj):
        return obj.get_profile_image()

    def get_sex(self, obj):
        return obj.get_sex()

    def get_birth(self, obj):
        if obj.birth:
            return get_datetime_str(obj.birth)

    def get_authorised(self, obj):
        return obj.get_authorised()

    def get_category(self, obj):
        return general_serializer.CategorySerializer(obj.category).data

    def get_categories(self, obj):
        return general_serializer.CategorySerializer(obj.categories, many=True).data

    def get_city(self, obj):
        if obj.city:
            return obj.city.name
        else:
            return None

    def get_is_followed(self, obj):
        try:
            user = self.context['user']
            if not user.is_anonymous():
                return obj.check_if_followed_by(follower=user)
            else:
                return False
        except KeyError:
            return False

    class Meta:
        model = models.UserProfile
        fields = ['id', 'authorised', 'username', 'first_name', 'last_name', 'name', 'heading', 'summary',
                  'profile_image', 'sex', 'birth', 'category', 'categories',
                  'location', 'is_followed', 'city']


class UserProfilePublicSerializer(UserProfileBaseSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.get_email_if_allowed()

    def get_phone(self, obj):
        return obj.get_phone_if_allowed()

    def get_followers_count(self, obj):
        return models.UserFollower.get_followers_count(user=obj.user)

    class Meta(UserProfileBaseSerializer.Meta):
        model = models.UserProfile
        fields = UserProfileBaseSerializer.Meta.fields + ['email', 'phone', 'permission_phone_public',
                                                          'permission_email_public', 'followers_count']


class UserProfileDetailSerializer(UserProfileBaseSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    feeds = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.get_email()

    def get_phone(self, obj):
        return obj.get_phone()

    def get_feeds(self, obj):
        from broadcast.serializers import BroadCastFeedSerializer
        return BroadCastFeedSerializer(obj.get_feeds(), many=True).data

    class Meta(UserProfileBaseSerializer.Meta):
        model = models.UserProfile
        fields = UserProfileBaseSerializer.Meta.fields + ['email', 'phone', 'signup_stage', 'signup_done', 'feeds',
                                                          'permission_phone_public', 'permission_email_public',
                                                          'read_notification_count',
                                                          'permission_stories_updates', 'permission_brands_updates',
                                                          'permission_events_updates', 'permission_product_updates']


class UserNotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return UserMiniSerializer(obj.sender).data

    class Meta:
        model = models.UserNotification
        exclude = []
