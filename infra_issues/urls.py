from django.urls import path
from . import views

urlpatterns = [
    path('file_issue/', views.file_complaint, name='file_complaint'),
]
