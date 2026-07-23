from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils import timezone
from decimal import Decimal  # Import Decimal


class SoftDeleteManager(models.Manager):
    """Default manager: only returns rows that haven't been sent to the recycle bin."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """
    Adds a recycle-bin: `delete()` marks a row as deleted instead of removing it,
    so it can be restored later from the Django admin. Use `hard_delete()` for a
    real, permanent delete (e.g. emptying the recycle bin).
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class Student(SoftDeleteModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    matric_number = models.CharField(max_length=20, unique=True)
    instrument = models.CharField(max_length=50)

    def delete(self, *args, **kwargs):
        for assessment in Assessment.objects.filter(student=self):
            assessment.delete()
        ca = CA.objects.filter(student=self).first()
        if ca:
            ca.delete()
        grade = Grade.objects.filter(student=self).first()
        if grade:
            grade.delete()
        super().delete(*args, **kwargs)

    def restore(self):
        for assessment in Assessment.all_objects.filter(student=self, is_deleted=True):
            assessment.restore()
        ca = CA.all_objects.filter(student=self, is_deleted=True).first()
        if ca:
            ca.restore()
        super().restore()
        grade = Grade.all_objects.filter(student=self, is_deleted=True).first()
        if grade:
            grade.restore()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.matric_number})"


class Assessment(SoftDeleteModel):
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

    def restore(self):
        super().restore()
        Grade.update_or_create_for_student(self.student)

    def __str__(self):
        return f"Assessment of {self.student} by {self.assessor} - Total: {self.total}"


class CA(SoftDeleteModel):
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

    def restore(self):
        super().restore()
        Grade.update_or_create_for_student(self.student)

    def __str__(self):
        return f"Assessment of {self.student}"


class Grade(SoftDeleteModel):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    ca = models.OneToOneField(CA, on_delete=models.CASCADE, null=True, blank=True)
    extra = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    @staticmethod
    def update_or_create_for_student(student):
        avg_total = Assessment.objects.filter(student=student).aggregate(Avg('total'))['total__avg'] or Decimal(0.00)
        ca = CA.objects.filter(student=student).first()

        # Use all_objects: a soft-deleted Grade row still occupies the unique
        # `student` slot, so get_or_create must see it to avoid a duplicate-key error.
        grade, created = Grade.all_objects.get_or_create(student=student, defaults={"ca": ca})

        grade.score = Decimal(avg_total)
        grade.ca = ca  # Update CA
        grade.total = grade.score + (Decimal(grade.ca.total) if grade.ca else Decimal(0)) + Decimal(grade.extra)
        grade.save()

    def save(self, *args, **kwargs):
        self.total = Decimal(self.score) + (Decimal(self.ca.total) if self.ca else Decimal(0)) + Decimal(self.extra)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Grade for {self.student} - Total: {self.total}"


class DeletedStudent(Student):
    """Proxy model powering the 'Deleted Students' recycle bin in the admin."""

    class Meta:
        proxy = True
        verbose_name = "Deleted Student"
        verbose_name_plural = "Deleted Students (Recycle Bin)"
