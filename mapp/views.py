# musicapp/views.py
from django.http import HttpResponse
from .models import Grade, Student, Assessment
from .forms import AssessmentForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Student, Assessment
from .forms import AssessmentForm, StudentSearchForm
import logging
from docx import Document

logger = logging.getLogger(__name__)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')

def end(request):
    return render(request, 'end.html')


def search_student(request):
    if request.method == 'POST':
        form = StudentSearchForm(request.POST)
        if form.is_valid():
            matric_suffix = form.cleaned_data.get('matric_suffix')
            logger.debug(f"Searching for matric suffix: {matric_suffix}")
            students = Student.objects.filter(matric_number__icontains=matric_suffix)
            return render(request, 'search_results.html', {'students': students, 'matric_suffix': matric_suffix})
        else:
            logger.debug(f"Form errors: {form.errors}")
    else:
        form = StudentSearchForm()

    return render(request, 'search_student.html', {'form': form})


@login_required
def assess_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.assessor = request.user
            assessment.student = student
            assessment.save()
            return redirect('student_assessment_list', student_id=student.id)
    else:
        form = AssessmentForm(initial={'student': student})

    return render(request, 'assess_student.html', {'form': form, 'student': student})

@login_required
def student_assessment_list(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    assessments = Assessment.objects.filter(student=student)
    grade = Grade.objects.filter(student=student).first()

    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.assessor = request.user
            assessment.student = student
            assessment.save()
            return redirect('end')
    else:
        form = AssessmentForm()

    return render(request, 'student_assessment_list.html', {
        'student': student,
        'assessments': assessments,
        'form': form,
        'grade': grade,
    })

@login_required
def assessment_list(request):
    assessments = Assessment.objects.filter(assessor=request.user)
    return render(request, 'assessment_list.html', {'assessments': assessments})

def grades_list(request):
    grades = Grade.objects.all()
    return render(request, 'grades_list.html', {'grades': grades})


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