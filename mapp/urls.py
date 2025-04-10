# musicapp/urls.py

from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('logins', views.login_view, name='login'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('ca', views.ca, name='ca'),
    path('getca/<int:id>', views.getCA, name='getca'),
    path('student-data', views.studentData, name='studentData'),
    path('exam', views.exam, name='exam'),
    path('grade', views.grade, name='grades_list'),
    path('grades/', views.grades_list, name='grades_list'),
    path('download-grades/', views.download_grades, name='download_grades'),
]
