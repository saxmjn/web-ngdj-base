from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
import json

from authe.jwt_utils import JWTAuthentication
from app.utils import success_resp, error_resp, get_value_or_default, get_value_or_404
from . import models, tasks


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def import_contacts(request):
    try:
        contacts = get_value_or_404(request.data, 'contacts')
        contacts = json.loads(contacts)
        print(type(contacts))
        tasks.import_contacts_from_phone.delay(user_id=request.user.id, contacts=contacts)
        context = {"status": "success"}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def check_phone_import_recorded(request):
    try:
        recorded = models.UserContactsImport.check_phone_record(user=request.user)
        context = {"recorded": recorded}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)