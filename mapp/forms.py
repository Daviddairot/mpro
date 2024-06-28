# assessments/forms.py

from django import forms
from .models import Assessment

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['song1', 'song2', 'song3', 'dressing']


class StudentSearchForm(forms.Form):
    matric_suffix = forms.CharField(label='Last Four Digits of Matric Number', max_length=4)