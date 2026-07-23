from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from .models import Grade, Student, Assessment, CA

admin.site.site_header = "Musicology Admin"
admin.site.site_title = "Musicology Admin"
admin.site.index_title = "Musicology Admin"

@admin.action(description='Export selected assessments to Excel')
def export_assessments_to_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Assessments"

    headers = [
        'S/N', 'Assessor', 'First Name', 'Last Name', 'Matric Number', 'Instrument', 
        'Song 1', 'Song 2', 'Song 3', 'Dressing', 'Total'
    ]
    ws.append(headers)

    for idx, assessment in enumerate(queryset.select_related('student', 'assessor'), start=1):
        ws.append([
            idx,
            assessment.assessor.username if assessment.assessor else "N/A",
            assessment.student.first_name,
            assessment.student.last_name,
            assessment.student.matric_number,
            assessment.student.instrument,
            float(assessment.song1),
            float(assessment.song2),
            float(assessment.song3),
            float(assessment.dressing),
            float(assessment.total)
        ])

    for i, header in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(i)].width = max(10, len(header) + 2)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="assessments_export.xlsx"'
    wb.save(response)
    return response

@admin.action(description='Export selected grades to Excel')
def export_grades_to_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Grades"

    headers = ['S/N', 'Student', 'Matric Number', 'CA', 'Exam', 'Total']
    ws.append(headers)

    for idx, grade in enumerate(queryset.select_related('student', 'ca'), start=1):
        ws.append([
            idx,
            f"{grade.student.first_name} {grade.student.last_name}",
            grade.student.matric_number,
            float(grade.ca.total) if grade.ca else 0,
            float(grade.score),
            float(grade.total)
        ])

    for i, header in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(i)].width = max(10, len(header) + 2)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="grades_export.xlsx"'
    wb.save(response)
    return response


class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'matric_number', 'instrument')
    search_fields = ('first_name', 'last_name', 'matric_number', 'instrument')

class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'song1', 'song2', 'song3', 'dressing', 'assessor', 'total')
    search_fields = ('student__matric_number', 'student__first_name', 'student__last_name')
    list_filter = ('assessor',)
    actions = [export_assessments_to_excel]

class CAAdmin(admin.ModelAdmin):
    list_display = ('student', 'CBT', 'practical', 'classwork', 'Assignment', 'total', 'assessor')
    search_fields = ('student__matric_number', 'student__first_name', 'student__last_name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'score', 'ca', 'extra', 'total')
    search_fields = ('student__first_name', 'student__last_name', 'student__matric_number')
    list_filter = ('student__instrument',)
    readonly_fields = ('score', 'total')
    autocomplete_fields = ('student', 'ca')
    actions = [export_grades_to_excel]

admin.site.register(Student, StudentAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(CA, CAAdmin)
