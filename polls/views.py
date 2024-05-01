from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from .forms import LoginForm, LecturerRegistrationForm, StudentRegistrationForm, AssignmentForm
from .forms import SubmissionForm
from .models import Lecturer, Student, Course, Assignment,Submission,GradeReport
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
import json

def register_lecturer(request):
    if request.method == 'POST':
        form = LecturerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the lecturer after registration
            return redirect('lecturer_dashboard')  # Redirect to the lecturer's dashboard
    else:
        form = LecturerRegistrationForm()
    return render(request, 'lecturer_register.html', {'form': form})

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the student after registration
            return redirect('student_dashboard')  # Redirect to the student's dashboard
    else:
        form = StudentRegistrationForm()
    return render(request, 'student_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'lecturer'):
                    return redirect('lecturer_dashboard')
                elif hasattr(user, 'student'):
                    return redirect('student_dashboard')
                return HttpResponseRedirect('/')  # Or some other default page
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Placeholder views for dashboards
def lecturer_dashboard(request):
    # Add logic to fetch necessary data for the lecturer's dashboard
    return render(request, 'lecturer_dashboard.html')

def student_dashboard(request):
    # Add logic to fetch necessary data for the student's dashboard
    return render(request, 'student_dashboard.html')

@login_required
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            # Extracting form data
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            due_date = form.cleaned_data['due_date']
            keywords = form.cleaned_data['keywords']
            marking_scheme = form.cleaned_data['marking_scheme']
            
            # Creating assignment
            try:
                course = form.cleaned_data['course']
                lecturer = request.user.lecturer
                assignment = Assignment.objects.create(
                    course=course,
                    lecturer=request.user,
                    title=title,
                    description=description,
                    due_date=due_date,
                    keywords=keywords,
                    marking_scheme=marking_scheme
                )
                messages.success(request, 'Assignment successfully created.')
                return redirect('view_assignments')
            except ObjectDoesNotExist:
                # Handle the case where the course does not exist
                # You can redirect the user to an error page or do whatever is appropriate
                messages.error(request, 'Course does not exist.')
                return redirect('create_assignment')
    else:
        form = AssignmentForm()
      
    return render(request, 'create_assignment.html', {'form': form})
@login_required
def lecturer_view(request):
    # Check if the user is a lecturer
    try:
        lecturer = request.user.lecturer
        assignments = Assignment.objects.filter(lecturer=lecturer.user)
        courses = Course.objects.filter(lecturer=lecturer.user)
    except Lecturer.DoesNotExist:
        # If the user is not a lecturer, initialize empty lists
        assignments = []
        courses = []
    
    return render(request, 'lecturer_view.html', {'assignments': assignments, 'courses': courses})
@login_required

def view_assignments(request):
    # Retrieve all assignments from the database
    assignments = Assignment.objects.all()
    
    return render(request, 'view_Assignments.html', {'assignments': assignments})
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'assignment_detail.html', {'assignment': assignment})
def grader(content, assignment):
    marking_scheme = assignment.marking_scheme
    score = 0
    for criterion, weight in marking_scheme.items():
        
        if criterion in content:
            score += weight
    return score



@login_required
def grade_submission(request, content, submission, student, assignment):
    marking_scheme = assignment.marking_scheme
    total_marks = sum(int(value) for value in marking_scheme.values() if isinstance(value, int))

    score = grader(content, marking_scheme) if total_marks != 0 else 0
    grade_percentage = (score / total_marks) * 100 if total_marks != 0 else 0

    submission.score = score
    submission.save()

    grade_report = GradeReport.objects.create(
        student=student,
        assignment=assignment,
        grade=score,
    )

    grade_report.save()


@login_required
def submit_work(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    student = request.user.student
    
    if request.method == 'POST':
        # Extract content from the request
        content = request.POST.get('content')

        # Save the submission
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.assignment = assignment
            submission.save()

            # Grade the submission
            grade_submission(request, content, submission, student, assignment)

            return HttpResponseRedirect('/polls/assignment/{}/'.format(pk))

    else:
        form = SubmissionForm()
    
    return render(request, 'submit_work.html', {'form': form})

@login_required
def view_grades(request):
    try:
        student = request.user.student
        grades = GradeReport.objects.filter(student=student)
    except Student.DoesNotExist:
        grades = []
    
    return render(request, 'view_grades.html', {'grades': grades})

@login_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    return render(request, 'view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required
def grades(request):
    try:
        lecturer = request.user.lecturer
        grades = GradeReport.objects.filter(assignment__lecturer=lecturer.user)
    except Lecturer.DoesNotExist:
        grades = []
    
    return render(request, 'grades.html', {'grades': grades})

def calculate_lecturer_grade(assignment):
    # Get all submissions for the assignment
    submissions = GradeReport.objects.filter(assignment=assignment)

    # Calculate the total score for all submissions
    total_score = sum(submission.grade for submission in submissions)

    # Calculate the average score
    if submissions.exists():
        average_score = total_score / submissions.count()
    else:
        average_score = 0

    return average_score