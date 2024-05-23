import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import InfraIssue

BASE_DIR = settings.BASE_DIR


@csrf_exempt
@api_view(['POST'])
def file_complaint(request):
    data = request.data
    if 'complex_name' not in data or 'room' not in data or 'issue' not in data or 'user' not in data:
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    # Extracting data from the request
    complex_name = data['complex_name']
    room = data['room']
    issue = data['issue']
    user = data['user']

    # Check if image file is included in the request
    if 'image' not in request.FILES:
        return Response({'error': 'Image file is missing'}, status=status.HTTP_400_BAD_REQUEST)

    # Save the image file
    image_file = request.FILES['image']
    # Here you can save the image file to your desired location or handle it as needed.
    image_path = os.path.join(BASE_DIR, 'images', image_file.name)
    with open(image_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)

    # Save other complaint details to the database
    date = datetime.date.today()
    InfraIssue.objects.create(
        complex_name=complex_name, room=room, issue=issue, user=user, date=date)

    # Handle Google Sheets integration (unchanged from your original code)
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.path.join(BASE_DIR, 'infra_issues',
                         'infra-app-420117-111af392d615.json'),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1m8qfH4aT8PF4gt4xrt5KLwmOLfXCWT_elIT7Ka8WZ7I'
        values = [
            [complex_name, room, issue, user,
                date.strftime('%d-%m-%Y'), 'Pending']
        ]
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range='Sheet1', valueInputOption='RAW', body={'values': values}).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Rollback database changes if any error occurs
        InfraIssue.objects.filter(
            complex_name=complex_name, room=room, issue=issue, user=user, date=date).delete()
        return Response({'error': f'Failed to file complaint. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Complaint filed successfully'}, status=status.HTTP_201_CREATED)
