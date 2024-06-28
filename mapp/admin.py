# assessments/admin.py

from django.contrib import admin
from .models import Grade, Student, Assessment

class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'matric_number', 'instrument')
    search_fields = ('first_name', 'last_name', 'matric_number', 'instrument')

class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'song1', 'song2', 'song3', 'dressing', 'assessor', 'total')
    search_fields = ('student__matric_number', 'student__first_name', 'student__last_name')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'score', 'ca', 'extra', 'total')
    search_fields = ('student__first_name', 'student__last_name', 'student__matric_number')
    list_filter = ('student__instrument',)
    readonly_fields = ('score', 'total')
    autocomplete_fields = ('student',)

admin.site.register(Student, StudentAdmin)
admin.site.register(Assessment, AssessmentAdmin)
