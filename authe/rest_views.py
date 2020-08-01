import logging
#
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
# Project
from commune.utils import get_value_or_404, get_value_or_default, create_error_object, success_resp, error_resp, \
    raise_error
from . import utils, jwt_utils
from user import models as user_models
from user import serializers as user_serializers

logger = logging.getLogger(__name__)


class Auth(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        email = get_value_or_default(request.GET, 'email', None)
        phone = get_value_or_default(request.GET, 'phone')

        try:
            context = utils.auth_verification(email=email, phone=phone)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            errors = create_error_object(str(ve))
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            errors = str(e)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        email = get_value_or_default(request.data, 'email', None)
        phone = get_value_or_default(request.data, 'phone')
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)
        phone_otp = get_value_or_default(request.data, 'phone_otp', None)
        email_otp = get_value_or_default(request.data, 'email_otp', None)

        try:
            context = utils.auth_signup(username=username, email=email, phone=phone, first_name=first_name,
                                                last_name=last_name, password1=password1,
                                                password2=password2, phone_otp=phone_otp, email_otp=email_otp)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            errors = create_error_object(str(ve))
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            errors = str(e)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        email = get_value_or_default(request.data, 'email', None)
        phone = get_value_or_default(request.data, 'phone', None)
        password = get_value_or_404(request.data, 'password')

        try:
            context = utils.auth_signin(email=email, phone=phone, password=password)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

class EmailAuth(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, format=None):
        email = get_value_or_404(request.data, 'email')
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        phone = get_value_or_default(request.data, 'phone')
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)
        otp = get_value_or_default(request.data, 'otp', None)

        try:
            context = utils.create_user_from_email(username=username, email=email, first_name=first_name,
                                                last_name=last_name, password1=password1,
                                                password2=password2, otp=otp, phone=phone)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            errors = create_error_object(str(ve))
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            errors = str(e)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        email = get_value_or_404(request.data, 'email')
        password = get_value_or_404(request.data, 'password')
        try:
            context = utils.get_user_from_email(email=email, password=password)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)        

class PhoneAuth(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, format=None):
        phone = get_value_or_404(request.data, 'phone_number')
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        email = get_value_or_default(request.data, 'email', None)
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)
        otp = get_value_or_default(request.data, 'otp')

        try:
            context = utils.create_user_from_phone(phone=phone, username=username,
                                                       email=email, first_name=first_name,
                                                last_name=last_name, password1=password1,
                                                password2=password2, otp=otp)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        phone = get_value_or_404(request.data, 'phone_number')
        password = get_value_or_404(request.data, 'password')

        try:
            context = utils.get_user_from_phone(phone=phone, password=password)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


class PhoneOTPAuth(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, format=None):
        phone = get_value_or_404(request.data, 'phone_number')
        otp = get_value_or_404(request.data, 'otp')

        try:
            user =  user_models.UserProfile.create_with_phone(phone=phone, email=None, first_name=None, last_name=None, username=None, otp=otp).user
            token = jwt_utils.get_token_for_user(user)
            userprofile = user_serializers.UserProfileDetailSerializer(user.userprofile).data
            data = {'username': user.username, 'token': token, 'user_id': user.id, 'user': userprofile}
            return Response(success_resp(data=data), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        phone = get_value_or_404(request.data, 'phone_number')
        otp = get_value_or_404(request.data, 'otp')

        try:
            context = utils.get_user_from_phone(phone=phone, phone_otp=otp)
            context['user'] = user_serializers.UserProfileDetailSerializer(context['user'].userprofile).data
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


class GoogleAuth(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, format=None):
        print(request.data)
        google_data = get_value_or_404(request.data, 'google_data')
        try:
            token = utils.get_or_create_user_from_google(data=google_data)
            context = {'token': token}
            return Response(context, status=status.HTTP_200_OK)
        except ValueError as ve:
            errors = create_error_object(str(ve))
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class LinkedinAuth(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, format=None):
        code = get_value_or_404(request.data, 'code')
        redirect_uri = get_value_or_404(request.data, 'redirect_uri')
        try:
            token = utils.get_or_create_user_from_linkedin(code=code, redirect_uri=redirect_uri)
            context = {'token': token}
            return Response(context, status=status.HTTP_200_OK)
        except ValueError as ve:
            errors = create_error_object(str(ve))
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def linkedin_auth_mobile(request):
    user_id = get_value_or_404(request.data, 'user_id')
    email = get_value_or_404(request.data, 'email')
    first_name = get_value_or_404(request.data, 'first_name')
    last_name = get_value_or_404(request.data, 'last_name')
    profile_image = get_value_or_default(request.data, 'profile_image', None)
    try:
        token = utils.get_or_create_user_from_linkedin_mob(
            user_id=user_id, email=email, first_name=first_name, last_name=last_name, profile_image=profile_image)
        context = {'token': token}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        errors = create_error_object(str(ve))
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        errors = str(e)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    try:
        operation = get_value_or_404(request.data, 'operation')
        phone = get_value_or_404(request.data, 'phone')
        OTP = get_value_or_default(request.data, 'OTP', None)
        email = get_value_or_default(request.data, 'email', None)
        password = get_value_or_default(request.data, 'password', None)
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)
        context = utils.registration(operation=operation, phone=phone, OTP=OTP, first_name=first_name, last_name=last_name, email=email, password=password)
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([jwt_utils.JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_password(request):
    try:
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        if password1 != password2:
            raise_error('ERR-AUTH-004')

        request.user.set_password(password1)
        request.user.save()
        context = {'message': 'Password successfully changed'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([jwt_utils.JWTAuthentication])
@permission_classes([IsAuthenticated])
def reset_password(request):
    try:
        old_password = get_value_or_404(request.data, 'old_password')
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')

        utils.reset_password(user=request.user, old_password=old_password, password1=password1, password2=password2)
        context = {'message': 'Password successfully changed'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([jwt_utils.JWTAuthentication])
@permission_classes([IsAuthenticated])
def forgot_password(request):
    try:
        email_otp = get_value_or_default(request.data, 'email_otp', None)
        phone_otp = get_value_or_default(request.data, 'phone_otp', None)
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')

        utils.forgot_password(user=request.user, password1=password1, password2=password2, email_otp=email_otp, phone_otp=phone_otp)
        context = {'message': 'Password successfully changed'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_anonymous(request):
    try:
        email_otp = get_value_or_default(request.data, 'email_otp', None)
        phone_otp = get_value_or_default(request.data, 'phone_otp', None)
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        email = get_value_or_default(request.data, 'email')
        phone = get_value_or_default(request.data, 'phone')

        utils.forgot_password_anonymous(password1=password1, password2=password2, email_otp=email_otp, phone_otp=phone_otp, email=email, phone=phone)
        context = {'message': 'Password successfully changed'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)