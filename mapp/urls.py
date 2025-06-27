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
    path('getUser', views.getUser, name='getUser'),
    path('grade', views.grade, name='grades_list'),
    path('grades/', views.grades_list, name='grades_list'),
    path('import-student', views.import_students_from_docx, name = 'import_students_from_docx'),
    path('import-classwork', views.import_classwork_scores, name ='import_classwork_scores'),
    path('import-CBT', views.import_cbt_scores, name ='import_CBT'),
    path('import-practical', views.import_practical_scores, name='import_practical_scores'),
    path('download-grades/', views.download_grades, name='download_grades'),
]
