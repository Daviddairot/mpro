# musicapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('home/', views.home, name='home'),
    path('search/', views.search_student, name='search_student'),
    path('assess/<int:student_id>/', views.assess_student, name='assess_student'),
    path('assessments/<int:student_id>/', views.student_assessment_list, name='student_assessment_list'),
    path('assessments/', views.assessment_list, name='assessment_list'),
    path('grades/', views.grades_list, name='grades_list'),
    path('download-grades/', views.download_grades, name='download_grades'),
    path('end/', views.end, name="end"),
]
