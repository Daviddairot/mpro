# musicapp/views.py
from django.http import HttpResponse

from mapp.utils import get_tokens_for_user
from .models import Grade, Student, Assessment
from .forms import AssessmentForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Student, Assessment, CA
from .forms import AssessmentForm, StudentSearchForm
import logging
from docx import Document
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    user = User.objects.create_user(username=username, password=password)
    tokens = get_tokens_for_user(user)
    return Response({'message': 'User created successfully', 'tokens': tokens})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    tokens = get_tokens_for_user(user)

    students = Student.objects.all()
    
    studentData = [
        {
            'id': student.id,
            'firstName': student.first_name or "NULL",
            'lastName': student.last_name or "NULL",
            'matricNumber': student.matric_number or "NULL",
            'instrument': student.instrument or "NULL"
        }
        for student in students
    ]
    return Response({'message': 'Login successful', 'tokens': tokens, 'students': studentData})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ca(request):
    user = request.user
    student_id = request.data.get('student')  # Assuming student is passed as an ID
    CBT = request.data.get('CBT')
    practical = request.data.get('practical')
    AH = request.data.get('AH')
    Assignments = request.data.get('Assignments')
    print(student_id)
    # Get Assessor (User)
    try:
        assessor = User.objects.get(username=user.username)
    except User.DoesNotExist:
        return Response({'error': 'Invalid Assessor'}, status=status.HTTP_400_BAD_REQUEST)

    # Get Student
    student = get_object_or_404(Student, id=student_id)
    print(student)
    # Get or create CA record
    ca, created = CA.objects.get_or_create(student=student)
    print(ca)
    # Assign assessor
    ca.assessor = assessor
    

    # Update only if a value is provided
    if CBT is not None:
        ca.CBT = CBT
    if practical is not None:
        ca.practical = practical
    if AH is not None:
        ca.AH = AH
    if Assignments is not None:
        ca.Assignment = Assignments  # Make sure field name matches your model

    ca.save()

    return Response({'message': 'Success'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCA(request, id):
    user = request.user
    stud = get_object_or_404(Student, id=id)
    student, created = CA.objects.get_or_create(student=stud)
    studentData = [
        {
            # 'id': student.id,
            'firstName': student.student.first_name or "NULL",
            'lastName': student.student.last_name or "NULL",
            'matricNumber': student.student.matric_number or "NULL",
            'instrument': student.student.instrument or "NULL",
            "CBT": student.CBT,
            "practical": student.practical,
            "AH": student.AH,
            "Assignment": student.Assignment,
            "total": student.total
        }
    ]
    return Response({'ca':studentData}, status=200)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def exam(request):
    user = request.user
    student_id = request.data.get('student')
    song1 = request.data.get('song1')
    song2 = request.data.get('song2')
    song3 = request.data.get('song3')
    dressing = request.data.get('dressing')
    
    # Get student
    student = get_object_or_404(Student, id=student_id)

    # Create assessment
    examData = {
        'song1': song1,
        'song2': song2,
        'song3': song3,
        'dressing': dressing,
        'student': student,
        'assessor': user,
    }

    assessment = Assessment.objects.create(**examData)
    
    return Response({'message': 'success'}, status=201)



def grades_list(request):
    grades = Grade.objects.all()
    return Response({'grades': grades}, status=201)


def download_grades(request):
    # Create a Word document
    doc = Document()
    doc.add_heading('Grade List', 0)

    # Add a table with columns: S/N, Student, Matric Number, Score, CA, Extra, Total
    table = doc.add_table(rows=1, cols=7)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'S/N'
    hdr_cells[1].text = 'Student'
    hdr_cells[2].text = 'Matric Number'
    hdr_cells[3].text = 'Score'
    hdr_cells[4].text = 'CA'
    hdr_cells[5].text = 'Extra'
    hdr_cells[6].text = 'Total'

    # Add data rows
    for idx, grade in enumerate(Grade.objects.all(), start=1):
        row_cells = table.add_row().cells
        row_cells[0].text = str(idx)
        row_cells[1].text = f"{grade.student.first_name} {grade.student.last_name}"
        row_cells[2].text = grade.student.matric_number
        row_cells[3].text = str(grade.score)
        row_cells[4].text = str(grade.ca)
        row_cells[5].text = str(grade.extra)
        row_cells[6].text = str(grade.total)

    # Create a response with the document
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=grades.docx'
    doc.save(response)
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def studentData(request):
    user = request.user
    assessor =  get_object_or_404(User, username=user)
    if assessor is None:
        return Response({'error': 'Invalid Assessor'}, status=status.HTTP_400_BAD_REQUEST)
    students = Student.objects.all()
    studentData = [
        {
            'id': student.id,
            'firstName': student.first_name or "NULL",
            'lastName': student.last_name or "NULL",
            'matricNumber': student.matric_number or "NULL",
            'instrument': student.instrument or "NULL"
        }
        for student in students
    ]
    return Response({'message': 'all registered student', 'students': studentData})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grade(request):
    user = request.user
    assessor =  get_object_or_404(User, username=user)
    if assessor is None:
        return Response({'error': 'Invalid Assessor'}, status=status.HTTP_400_BAD_REQUEST)
    grades = Grade.objects.all()
    gradeData = [
        {
            'id': grade.id,
            'extra': grade.extra,
            'firstname': grade.student.first_name,
            'lastname':grade.student.last_name,
            'matric_number': grade.student.matric_number,
            'CA': grade.ca.total,
            'Exam': grade.score,
            'total': grade.total
        }
        for grade in grades
    ]
    return Response({'message': 'all grades', 'grades': gradeData})