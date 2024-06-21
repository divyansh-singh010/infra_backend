import datetime
from django.shortcuts import redirect
from openpyxl import Workbook
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .models import InfraIssue, Profile
from PIL import Image
from django.contrib.auth.models import User
from .utils import generate_tokens
from django.http import HttpResponse
from django.db.models import Count


@csrf_exempt
@api_view(['POST'])
def file_complaint(request):
    if not request.user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    required_fields = ['complex_name', 'room', 'issue']

    # Check if all required fields are present in the request data
    if not all(field in data for field in required_fields):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    # Extracting data from the request
    complex_name = data['complex_name']
    room = data['room']
    issue = data['issue']
    user = request.user.username
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
        issue = InfraIssue.objects.create(
            complex_name=complex_name, room=room, issue=issue, user=user, date=date, image=image_file)
        return Response({'message': 'Complaint filed successfully', 'id': issue.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'Failed to save complaint to the database. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
def get_queries(request):
    if not request.user.is_staff:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        queries = list(InfraIssue.objects.all().values().order_by('-date'))

        room_frequency = InfraIssue.objects.values(
            'room').annotate(freq=Count('room')).order_by('-freq')
        complex_frequency = InfraIssue.objects.values('complex_name').annotate(
            freq=Count('complex_name')).order_by('-freq')
        issue_frequency = InfraIssue.objects.values(
            'issue').annotate(freq=Count('issue')).order_by('-freq')

        return Response({
            'queries': queries,
            'room_frequency': list(room_frequency),
            'complex_frequency': list(complex_frequency),
            'issue_frequency': list(issue_frequency),
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("An error occurred:", e)
        return Response({'error': f'Failed to fetch queries. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
def login(request):

    code = request.query_params.get('code')

    token_url = 'https://oauth.iitd.ac.in/token.php'
    resource_url = 'https://oauth.iitd.ac.in/resource.php'

    response = requests.post(token_url, data={
                             'client_id': '2HEtZsBPc0gWWDph0kBijGm8uWKeHOn1', 'client_secret': 'eHv9wrbfJBonzqAc4P0hQP9jSul1lfeJ', 'grant_type': 'authorization_code', 'code': code})
    if response.status_code != 200:
        return Response({'error': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)

    response = response.json()

    resource = requests.post(
        resource_url, data={'access_token': response['access_token']})

    if resource.status_code != 200:
        return Response({'error': 'Login failed'}, status=status.HTTP_400_BAD_REQUEST)

    resource = resource.json()

    if not User.objects.filter(username=resource['user_id']).exists():
        print("User ID is ", resource['user_id'])
        user = User.objects.create(
            username=resource['user_id'], password=resource['uniqueiitdid'])
        if user.username == 'bb1221367' or user.username == 'ee1230728' or user.username == 'harshakota':
            user.is_staff = True
            user.is_superuser = True
            user.save()
        Profile.objects.create(
            user_id=user, entry_number=resource['uniqueiitdid'], name=resource['name'], email=resource['email'], category=resource['category'])

    user = User.objects.get(username=resource['user_id'])
    print("User ID is ", resource['user_id'])
    access_token = generate_tokens(user)['access']

    redirect_url = f'https://infraportal.iitd.ac.in/token?token={access_token}'
    return redirect(redirect_url)


@csrf_exempt
@api_view(['GET'])
def get_user_details(request):
    if not request.user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    profile = Profile.objects.get(user_id=user)
    return Response({'profile': {'name': profile.name, 'entry_number': profile.entry_number, 'email': profile.email, 'category': profile.category}}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['PUT'])
def update_status(request):
    if not request.user.is_staff:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    required_fields = ['id', 'status']

    if not all(field in data for field in required_fields):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    id = data['id']
    issue_status = data['status']
    try:
        issue = InfraIssue.objects.get(id=id)
        issue.status = issue_status
        issue.save()
        return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to update status. Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
def download_all_queries(request):
    if not request.user.is_staff:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        data = InfraIssue.objects.all().values(
            'id', 'complex_name', 'room', 'issue', 'date', 'status')

        wb = Workbook()
        ws = wb.active

        headers = ['id', 'complex_name', 'room', 'issue', 'date', 'status']
        ws.append(headers)

        for item in data:
            ws.append([item[field] for field in headers])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=infra_issues.xlsx'

        wb.save(response)

        return HttpResponse(response, status=status.HTTP_200_OK)
    except Exception as e:
        print("An error occurred:", e)
        return Response({'error': 'Failed to download queries', 'e': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
