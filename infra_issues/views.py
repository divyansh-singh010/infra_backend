import os
import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import InfraIssue
from PIL import Image

BASE_DIR = settings.BASE_DIR

@csrf_exempt
@api_view(['POST'])
def file_complaint(request):
    data = request.data
    required_fields = ['complex_name', 'room', 'issue', 'user']

    # Check if all required fields are present in the request data
    if not all(field in data for field in required_fields):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    # Extracting data from the request
    complex_name = data['complex_name']
    room = data['room']
    issue = data['issue']
    user = data['user']
    image_file = None

    # Handle image upload
    if 'image' in request.FILES:
        image_file = request.FILES['image']
        if image_file.name.endswith('.png'):
            image = Image.open(image_file)
            image = image.convert('RGB')
            image_file.name = image_file.name.replace('.png', '.jpg')

    # Save complaint details to the database
    date = datetime.date.today()
    try:
        InfraIssue.objects.create(
            complex_name=complex_name, room=room, issue=issue, user=user, date=date, image=image_file)
        return Response({'message': 'Complaint filed successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'Failed to save complaint to the database. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handle Google Sheets integration
    # try:
    #     credentials = service_account.Credentials.from_service_account_file(
    #         os.path.join(BASE_DIR, 'infra_issues', 'infra-app-420117-111af392d615.json'),
    #         scopes=['https://www.googleapis.com/auth/spreadsheets']
    #     )
    #     service = build('sheets', 'v4', credentials=credentials)
    #     spreadsheet_id = '1m8qfH4aT8PF4gt4xrt5KLwmOLfXCWT_elIT7Ka8WZ7I'
    #     values = [
    #         [complex_name, room, issue, user, date.strftime('%d-%m-%Y'), 'Pending']
    #     ]
    #     result = service.spreadsheets().values().append(
    #         spreadsheetId=spreadsheet_id, range='Sheet1', valueInputOption='RAW', body={'values': values}).execute()
    #     print('{0} cells updated.'.format(result.get('updatedCells')))
    # except Exception as e:
    #     # Rollback the database transaction if Google Sheets integration fails
    #     infra_issue.delete()
    #     return Response({'error': f'Failed to file complaint. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # return Response({'message': 'Complaint filed successfully'}, status=status.HTTP_201_CREATED)
