# DJANGO
from django.contrib.auth.models import User
import json
# REST
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
# PROJECT
from authe.jwt_utils import JWTAuthentication
from app.utils import get_value_or_404, get_value_or_default, success_resp, error_resp
from . import models, serializers


@api_view(['PUT'])
@permission_classes([AllowAny])
def check_phone_verification(request):
    phone = get_value_or_404(request.data, 'phone')
    operation = get_value_or_404(request.data, 'operation')
    OTP = get_value_or_default(request.data, 'OTP', None)
    try:
        data = models.UserProfile.phone_input(operation=operation, phone=phone, OTP=OTP)
        if operation == 'VERIFY_USER_PHONE':
            context = {'phone_verified': data['phone_verified']}
        elif operation == 'VERIFY_USER_REGISTRATION':
            context = {'user_registered': data['user_registered']}
        elif operation == 'SEND_PHONE_VERIFICATION_OTP':
            context = {'message': data['message']}
        elif operation == 'SEND_PHONE_VERIFICATION_OTP_ALLOW_ANY':
            context = {'message': data['message']}

        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_phone(request):
    phone = get_value_or_404(request.data, 'phone')
    OTP = get_value_or_404(request.data, 'OTP')
    try:
        data = request.user.userprofile.update_phone(phone=phone, OTP=OTP)
        return Response(success_resp(data=data), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_email(request):
    email = get_value_or_404(request.data, 'email')
    otp = get_value_or_404(request.data, 'otp')
    password = get_value_or_404(request.data, 'password')
    try:
        models.UserProfile.update_email(user=request.user, new_email=email, otp=otp, password=password)
        context = {'message': 'Email updated successfully'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_tags(request):
    tags = models.UserTag.get_tags()
    sdata = serializers.UserTagSerializer(tags, many=True).data
    return Response(sdata, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    sdata = serializers.UserSerializer(request.user).data
    return Response(sdata, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_all_users(request):
    try:
        offset = int(get_value_or_default(request.GET, 'offset', 0))
        user_profiles = models.UserProfile.get_users(offset=offset)
        sdata = serializers.UserProfileBaseSerializer(user_profiles, many=True, context={'user': request.user}).data
        context = {'users': sdata}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_users_suggestion(request):
    try:
        obj = models.UserProfile.get_users_suggestion()
        users = serializers.UserProfileBaseSerializer(obj['users'], many=True, context={'user': request.user}).data
        context = {'users': users, 'count': obj['count']}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['post'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_users_for_categories(request):
    category_ids = get_value_or_404(request.data, 'category_ids[]')
    offset = get_value_or_default(request.data, 'offset', 0)
    try:
        obj = models.UserProfile.get_users_for_categories(category_ids=category_ids, offset=offset)
        users = serializers.UserProfileBaseSerializer(obj['users'], many=True, context={'user': request.user}).data
        context = {'users': users, 'count': obj['count']}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_user_profile(request, username):
    user_profile = models.UserProfile.get_from_username(username)
    try:
        sdata = serializers.UserProfilePublicSerializer(user_profile, context={'user': request.user}).data
        data = {'user': sdata}
        return Response(success_resp(data=data), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user_profile = models.UserProfile.get_from_user(request.user)
        sdata = serializers.UserProfileDetailSerializer(user_profile).data
        return Response(sdata, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)
        email = get_value_or_default(request.data, 'email', None)
        profile_image = get_value_or_default(request.data, 'profile_image')
        heading = get_value_or_default(request.data, 'heading', None)
        summary = get_value_or_default(request.data, 'summary', None)
        city_code = get_value_or_default(request.data, 'city_code', None)
        location = get_value_or_default(request.data, 'location', None)
        birth = get_value_or_default(request.data, 'birth', None)
        sex = get_value_or_default(request.data, 'sex', None)
        category_code = get_value_or_default(request.data, 'category_code', None)
        category_code_list = get_value_or_default(request.data, 'category_code_list', None)
        permission_stories_updates = get_value_or_default(request.data, 'permission_stories_updates', None)
        permission_brands_updates = get_value_or_default(request.data, 'permission_brands_updates', None)
        permission_events_updates = get_value_or_default(request.data, 'permission_events_updates', None)
        permission_product_updates = get_value_or_default(request.data, 'permission_product_updates', None)
        permission_phone_public = get_value_or_default(request.data, 'permission_phone_public', None)
        permission_email_public = get_value_or_default(request.data, 'permission_email_public', None)
        device_token = get_value_or_default(request.data, 'device_token')

        if category_code_list:
            category_code_list = json.loads(category_code_list)

        print(category_code_list, type(category_code_list))

        try:
            user_profile = models.UserProfile.update(
                user=request.user, first_name=first_name, last_name=last_name, username=username,
                email=email,
                profile_image=profile_image,
                heading=heading, summary=summary, city_code=city_code, category_code=category_code,
                category_code_list=category_code_list,
                sex=sex, birth=birth, location=location,
                permission_stories_updates=permission_stories_updates,
                permission_brands_updates=permission_brands_updates,
                permission_product_updates=permission_product_updates,
                permission_events_updates=permission_events_updates,
                permission_phone_public=permission_phone_public, permission_email_public=permission_email_public,
                device_token=device_token
            )

            sdata = serializers.UserProfileDetailSerializer(user_profile).data
            return Response(sdata, status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_suggestions_list(request):
    try:
        data = request.user.userprofile.get_suggestions()
        connections = serializers.UserMiniSerializer(data['suggestions'], many=True).data
        context = {'connections': connections}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_connections_list(request):
    try:
        operation = get_value_or_404(request.GET, 'operation')
        data = models.UserFollower.get_connections(user=request.user, operation=operation)
        connections = serializers.UserMiniSerializer(data['connections'], many=True).data
        context = {'connections': connections, 'count': data['count']}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_people_list(request):
    try:
        code = get_value_or_404(request.GET, 'code')
        type = get_value_or_404(request.GET, 'type')
        data = models.UserFollower.get_people(user=request.user, code=code, type=type)
        connections = serializers.UserMiniConnectionSerializer(data['all'], many=True, context={'user': request.user}).data
        context = {'connections': connections}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_connections_list_in_common_param(request):
    try:
        parameter = get_value_or_404(request.GET, 'parameter')
        data = models.UserFollower.get_connections_with_common(user=request.user, parameter=parameter)
        connections = serializers.UserMiniConnectionSerializer(data['all'], many=True,
                                                               context={'user': request.user}).data
        context = {'connections': connections}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


class UserFollowerView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, username, format=None):
        try:
            followee = User.objects.get(username=username)
            data = models.UserFollower.update(followee=followee, follower=request.user)
            return Response(success_resp(data=data), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_status_feed(request):
    try:
        data = models.UserFollower.find_followings_and_status_updates(user=request.user)
        followings = serializers.UserProfileMiniSerializer(data['followings'], many=True).data
        context = {'followings': followings, 'count': data['count']}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_notification_feed(request):
    try:
        offset = get_value_or_default(request.GET, 'offset', 0)
        data = models.UserNotification.get_notifications(user=request.user, offset=offset)
        notifications = serializers.UserNotificationFeedSerializer(data['notifications'], many=True).data
        context = {'notifications': notifications, 'total_count': data['total_count'], 'read_count': data['read_count']}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_last_opened(request):
    try:
        request.user.userprofile.set_last_opened()
        context = {'message': 'success'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


class AdminUserProfileView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)
        email = get_value_or_default(request.data, 'email', None)
        profile_image = get_value_or_default(request.data, 'profile_image')
        heading = get_value_or_default(request.data, 'heading', None)
        summary = get_value_or_default(request.data, 'summary', None)
        location = get_value_or_default(request.data, 'location', None)
        sex = get_value_or_default(request.data, 'location', None)
        category_code = get_value_or_default(request.data, 'category_code', None)

        try:
            user_profile = models.UserProfile.admin_create(first_name=first_name, last_name=last_name, email=email,
                                                           username=username, profile_image=profile_image,
                                                           heading=heading, category_code=category_code, )
            sdata = serializers.UserProfileDetailSerializer(user_profile).data
            return Response(sdata, status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_info(request):
    user_id = get_value_or_404(request.GET, 'user_id')
    user = User.objects.get(id=user_id)
    sdata = serializers.UserDetailSerializer(user).data
    return Response(sdata, status=status.HTTP_200_OK)
