import logging
#
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
# Project
from authe.jwt_utils import JWTAuthentication
from commune.utils import get_value_or_404, create_error_object, success_resp, error_resp, get_value_or_default
from commune import _datetime as datetime
from commune import _analytics as analytics
from . import serializers, utils, models

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_otp(request):
    try:
        email = get_value_or_default(request.GET, 'email', None)
        phone = get_value_or_default(request.GET, 'phone', None)

        context = utils.get_otp(email=email, phone=phone)
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        errors = create_error_object(str(ve))
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        errors = str(e)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def post_file(request):
    bucket = get_value_or_404(request.data, 'bucket')
    file_name = get_value_or_404(request.data, 'file_name')
    try:
        file = models.File.store_public_file(bucket=bucket, file_name=file_name)
        context = {'file': file, 'message': 'success'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_categories(request):
    try:
        obj = models.Category.get_categories()
        categories = serializers.CategorySerializer(obj['categories'], many=True).data
        context = {'categories': categories, 'count': obj['count']}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        errors = create_error_object(str(ve))
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        errors = str(e)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities(request):
    try:
        obj = models.City.get_cities()
        cities = serializers.CitySerializer(obj['cities'], many=True).data
        context = {'cities': cities, 'count': obj['count']}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        errors = create_error_object(str(ve))
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        errors = str(e)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def post_contact_query(request):
    email = get_value_or_404(request.data, 'email')
    name = get_value_or_404(request.data, 'name')
    subject = get_value_or_404(request.data, 'subject')
    message = get_value_or_404(request.data, 'message')
    try:
        models.ContactQuery.create(email=email, name=name, subject=subject, message=message)
        context = {'message': 'success'}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        errors = create_error_object(str(ve))
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        errors = str(e)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def post_newsletter_subscriber(request):
    email = get_value_or_404(request.data, 'email')
    try:
        models.NewsletterSubscriber.create(email=email)
        context = {'message': 'success'}
        return Response(context, status=status.HTTP_200_OK)
    except ValueError as ve:
        errors = create_error_object(str(ve))
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        errors = str(e)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_datetime_vs_users(request):
    try:
        start = datetime.create_datetime_from_iso(get_value_or_default(request.data, 'start', None), 'Asia/Kolkata')
        end = datetime.create_datetime_from_iso(get_value_or_default(request.data, 'end', None), 'Asia/Kolkata')

        data = analytics.get_user_data_for_datetime(start=start, end=end)
        context = {"analytics": data}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_last_opened_info(request):
    try:
        start = datetime.create_datetime_from_iso(get_value_or_default(request.data, 'start', None), 'Asia/Kolkata')
        end = datetime.create_datetime_from_iso(get_value_or_default(request.data, 'end', None), 'Asia/Kolkata')

        count = analytics.get_last_opened_info(start=start, end=end)
        context = {"count": count}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)