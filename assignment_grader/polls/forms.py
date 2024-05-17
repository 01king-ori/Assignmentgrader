from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from .models import Lecturer, Student
from .models import User,Course
from .models import Submission
from .models import Assignment

class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class LecturerRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # Assuming lecturers might need staff access
        if commit:
            user.save()
            Lecturer.objects.create(user=user)
        return user

class StudentRegistrationForm(UserCreationForm):
    admission_number = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "admission_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admission_number'].required = True  # Set the admission_number field as required

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            student = Student.objects.create(user=user, admission_number=self.cleaned_data['admission_number'])
            return user  # Return only the user object
        return user

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['course', 'title', 'description', 'due_date', 'keywords', 'marking_scheme','min_words']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M:%S'),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['content']