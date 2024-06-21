from django.urls import path
from . import views

urlpatterns = [
    path('file_issue/', views.file_complaint, name='file_complaint'),
    path('queries/', views.get_queries, name='get_queries'),
    path('login/', views.login, name='login'),
    path('user/', views.get_user_details, name='get_user_details'),
    path('update_status/', views.update_status, name='update_status'),
    path('download/', views.download_all_queries, name='download_image')
]
