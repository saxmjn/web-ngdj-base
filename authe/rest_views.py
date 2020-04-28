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

logger = logging.getLogger(__name__)


class EmailAuth(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, format=None):
        email = get_value_or_404(request.data, 'email')
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)

        try:
            user = utils.create_user_from_email(username=username, email=email, first_name=first_name,
                                                last_name=last_name, password1=password1,
                                                password2=password2)
            context = {'username': user.username, 'password': password1}
            return Response(context, status=status.HTTP_200_OK)
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
        phone_number = get_value_or_404(request.data, 'phone_number')
        email = get_value_or_404(request.data, 'email')
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)

        try:
            user = utils.create_user_from_phone(phone_number=phone_number, username=username,
                                                       email=email, first_name=first_name,
                                                last_name=last_name, password1=password1,
                                                password2=password2)
            context = {'username': user.username, 'password': password1}
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        phone_number = get_value_or_404(request.data, 'phone_number')
        password = get_value_or_404(request.data, 'password')

        try:
            context = utils.get_user_from_phone(phone_number=phone_number, password=password)
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

        if not request.user.check_password(old_password):
            raise_error('ERR-AUTH-003')

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