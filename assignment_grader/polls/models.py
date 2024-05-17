from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.validators import MinLengthValidator

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=False)
    

class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    admission_number = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField()
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='courses')

    def __str__(self):
        return self.name

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    min_words = models.PositiveIntegerField(default=100)  # Default value added here
    keywords = models.TextField()  # Store keywords as comma-separated string
    marking_scheme = models.JSONField(default=dict) 

    def is_due(self):
        return timezone.now() > self.due_date

    def __str__(self):
        return self.title
class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    content = models.TextField(validators=[MinLengthValidator(1)])  # Ensure content is not empty
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)  # Store score after grading

    def is_late(self):
        return self.submitted_at > self.assignment.due_date

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"

class GradeReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    grade = models.FloatField()  # Store overall grade for the assignment
    feedback = models.TextField(blank=True)  # Optional feedback from lecturer

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title} - {self.grade}"
