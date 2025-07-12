from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from decimal import Decimal  # Import Decimal

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
        self.total = Decimal(self.song1) + Decimal(self.song2) + Decimal(self.song3) + Decimal(self.dressing)
        super().save(*args, **kwargs)
        Grade.update_or_create_for_student(self.student)

    def delete(self, *args, **kwargs):
        student = self.student
        super().delete(*args, **kwargs)
        Grade.update_or_create_for_student(student)

    def __str__(self):
        return f"Assessment of {self.student} by {self.assessor} - Total: {self.total}"

class CA(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    assessor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    CBT = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    practical = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    classwork = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    Assignment = models.DecimalField(decimal_places=2, max_digits=5, default=0.00)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)


    def save(self, *args, **kwargs):
        self.total = Decimal(self.CBT) + Decimal(self.practical) + Decimal(self.classwork) + Decimal(self.Assignment)
        super().save(*args, **kwargs)
        Grade.update_or_create_for_student(self.student)

    def delete(self, *args, **kwargs):
        student = self.student
        super().delete(*args, **kwargs)
        Grade.update_or_create_for_student(student)

    def __str__(self):
        return f"Assessment of {self.student}"

class Grade(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    ca = models.OneToOneField(CA, on_delete=models.CASCADE, null=True, blank=True)
    extra = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    @staticmethod
    def update_or_create_for_student(student):
        avg_total = Assessment.objects.filter(student=student).aggregate(Avg('total'))['total__avg'] or Decimal(0.00)
        ca = CA.objects.filter(student=student).first()

        grade, created = Grade.objects.get_or_create(student=student, defaults={"ca": ca})
        
        grade.score = Decimal(avg_total)
        grade.ca = ca  # Update CA
        grade.total = grade.score + (Decimal(grade.ca.total) if grade.ca else Decimal(0)) + Decimal(grade.extra)
        grade.save()

    def save(self, *args, **kwargs):
        self.total = Decimal(self.score) + (Decimal(self.ca.total) if self.ca else Decimal(0)) + Decimal(self.extra)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Grade for {self.student} - Total: {self.total}"
