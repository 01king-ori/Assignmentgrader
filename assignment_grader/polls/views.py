from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime,timedelta,timezone
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from .forms import LoginForm, LecturerRegistrationForm, StudentRegistrationForm, AssignmentForm
from .forms import SubmissionForm
from .count_words import count_words
from .keywords_marker import preprocess_text,calculate_similarity,mark_assignment
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
            admission_number = form.cleaned_data.get('admission_number')
            if admission_number.startswith('ECCI/'):
                user = form.save()
                login(request, user)  # Automatically log in the student after registration
                return redirect('student_dashboard')  # Redirect to the student's dashboard
            else:
                messages.error(request, 'you do not belong in this system')
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
                lecturer = request.user.lecturer  # Get the lecturer instance
                assignment = Assignment.objects.create(
                    course=course,
                    lecturer=lecturer,  # Change to lecturer instance
                    title=title,
                    description=description,
                    due_date=due_date,
                    keywords=keywords,
                    marking_scheme=marking_scheme
                )
                messages.success(request, 'Assignment successfully created.')
                return redirect('lecturer_dashboard')
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
    lecturer = request.user.lecturer
    
    
    assignments = Assignment.objects.filter(lecturer=lecturer)
    
    
    courses = Course.objects.filter(lecturer=lecturer)
    
    
    no_assignments_message = None
    
    if not assignments:
        no_assignments_message = "No assignments created"
    
    return render(request, 'lecturer_view.html', {'assignments': assignments,  'no_assignments_message': no_assignments_message})
@login_required
def view_assignments(request):
    # Retrieve all assignments from the database
    assignments = Assignment.objects.all()
    
    return render(request, 'view_Assignments.html', {'assignments': assignments})
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    return render(request, 'assignment_detail.html', {'assignment': assignment})
@login_required
def submit_work(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    student = request.user.student
    
    # Check if the student has already submitted this assignment
    existing_submission = Submission.objects.filter(student=student, assignment=assignment).first()
    if existing_submission:
        return HttpResponse("You have already submitted your work for this assignment.")
    
    if request.method == 'POST':
        # Save the submission
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.assignment = assignment
            submission.save()
            
            # Grade the submission
            content = submission.content
            grade_submission(request, assignment, content, student)
            
            return HttpResponseRedirect('/polls/assignment/{}/'.format(pk))
    else:
        form = SubmissionForm()
    
    return render(request, 'submit_work.html', {'form': form})

def grader(content, assignment):
    marking_scheme = assignment.marking_scheme
    content_tokens = preprocess_text(content)
    score = 0

    for keyword in marking_scheme.get("keywords", []):
        if keyword.lower() in content.lower():
            score += marking_scheme.get("Correctness", 0)

    return score

def grade_submission(request, assignment, content, student):
    # Check if content is not empty
    if content.strip():
        # Retrieve keywords from the assignment
        expected_keywords = assignment.keywords.split(',')

        # Calculate similarity between the content and expected keywords
        similarity = calculate_similarity(content, expected_keywords)

        # Calculate the marks based on similarity
        marks = mark_assignment(content, expected_keywords)

        # Count the words in the submission
        word_count = count_words(content)

        if word_count >= assignment.min_words:
            marks += 10
        else:
            # Deduct 10 marks if word count is less than the minimum required words
            marks -= 10

        # Check for on-time submission
        if timezone.now() <= assignment.due_date:
            # Award 10 marks for on-time submission
            marks += 10
        else:
            # Deduct 10 marks for late submission
            marks -= 10

        # Save the submission
        submission = Submission.objects.create(
            student=student,
            assignment=assignment,
            content=content,
            score=marks
        )

        # Get the grade report if it exists, or create a new one
        grade_report, created = GradeReport.objects.get_or_create(
            student=student,
            assignment=assignment,
            defaults={'grade': marks}  # Set the default value for grade
        )

        # Update the grade if the grade report already exists
        if not created:
            grade_report.grade = marks
            grade_report.save()
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
        lecturer = Lecturer.objects.get(user=request.user)
        grades = GradeReport.objects.filter(assignment__lecturer=lecturer)
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
def register(request):
     return render(request, 'register.html')
@login_required
def view_reports(request):
    # Check if the logged-in user is a lecturer
   
    # Retrieve assignments associated with the logged-in lecturer
    assignments = Assignment.objects.filter(lecturer=request.user.lecturer)

    reports = []

    for assignment in assignments:
        passed_count = GradeReport.objects.filter(assignment=assignment, grade__gte=50).count()
        failed_count = GradeReport.objects.filter(assignment=assignment, grade__lt=50).count()
        reports.append({
            'assignment': assignment,
            'passed_count': passed_count,
            'failed_count': failed_count,
        })

    return render(request, 'reports.html', {'reports': reports})
@login_required
def student_dashboard(request):
   current_datetime =  timezone.now()
    # Calculate the datetime 1 days from now
   ten_days_from_now = current_datetime + timedelta(days=1)
   due_assignments = Assignment.objects.filter(due_date__lt=ten_days_from_now).order_by('due_date')
    # Calculate days until due for each assignment
   for assignment in due_assignments:
        assignment.days_until_due = (assignment.due_date - current_datetime).days
   context = {
        'assignments': due_assignments
    }
   return render(request, 'student_dashboard.html', context)