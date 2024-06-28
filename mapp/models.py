# musicapp/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    matric_number = models.CharField(max_length=20, unique=True)
    instrument = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.matric_number})"

class Assessment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assessor = models.ForeignKey(User, on_delete=models.CASCADE)
    song1 = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    song2 = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    song3 = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    dressing = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total = self.song1 + self.song2 + self.song3 + self.dressing
        super().save(*args, **kwargs)
        Grade.update_or_create_for_student(self.student)

    def delete(self, *args, **kwargs):
        student = self.student
        super().delete(*args, **kwargs)
        Grade.update_or_create_for_student(student)

    def __str__(self):
        return f"Assessment of {self.student} by {self.assessor} - Total: {self.total}"

class Grade(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    ca = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    extra = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    @staticmethod
    def update_or_create_for_student(student):
        # Calculate mean of the total scores from the assessments
        avg_total = Assessment.objects.filter(student=student).aggregate(Avg('total'))['total__avg'] or 0.00
        # Get or create the Grade instance
        grade, created = Grade.objects.get_or_create(student=student)
        grade.score = avg_total
        grade.total = grade.score + grade.ca + grade.extra
        grade.save()

    def save(self, *args, **kwargs):
        self.total = self.score + self.ca + self.extra
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Grade for {self.student} - Total: {self.total}"
