from .models import InfraIssue
import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import service_account
from googleapiclient.discovery import build


@api_view(['POST'])
def file_complaint(request):
    data = request.data
    if 'complex_name' not in data or 'room' not in data or 'issue' not in data or 'user' not in data:
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
    complex_name = data['complex_name']
    room = data['room']
    issue = data['issue']
    user = data['user']
    date = datetime.date.today()
    InfraIssue.objects.create(
        complex_name=complex_name, room=room, issue=issue, user=user, date=date)
    # also save all the details of the complaint in a google sheets file
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            '../infra_backend/infra_issues/infra-app-420117-111af392d615.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

        # Build the Google Sheets API service
        service = build('sheets', 'v4', credentials=credentials)

        # The ID of the spreadsheet to write to
        spreadsheet_id = '1m8qfH4aT8PF4gt4xrt5KLwmOLfXCWT_elIT7Ka8WZ7I'

        # The data to write to the spreadsheet
        values = [
            [complex_name, room, issue, user,
                date.strftime('%d-%m-%Y'), 'Pending']
        ]
        # the last cell should be 'Pending' as the status of the complaint and it should be the dropdown value

        print(values)
        # Call the Sheets API to update the spreadsheet
        # automatically write the cells in the next empty row
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range='Sheet1', valueInputOption='RAW', body={'values': values}).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))
    except Exception as e:
        # also print the error message in the console
        print(f"Error occurred: {str(e)}")
        return Response({'error': f'Failed to file complaint. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'message': 'Complaint filed successfully'}, status=status.HTTP_201_CREATED)
