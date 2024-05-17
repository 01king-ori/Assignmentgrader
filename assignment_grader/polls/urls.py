from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
     path('register/lecturer/', views.register_lecturer, name='register_lecturer'),
    path('register/student/', views.register_student, name='register_student'),
    path('register',views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('dashboard/lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    

    path('create_assignment/', views.create_assignment, name='create_assignment'),
    path('student_view/', views.create_assignment, name='student_view'),
    path('view_submissions/', views.view_submissions, name='view_submissions'),
     path('reports/', views.view_reports, name='view_reports'),
    path('view_grades/', views.view_grades, name='view_grades'),
    path('view_submissions/<int:assignment_id>/', views.view_submissions, name='view_submissions'),
    path('lecturer_view/',views.lecturer_view, name='lecturer_view'),
    path('grades/', views.grades, name='grades'),
    path('assignment/<int:pk>/', views.assignment_detail, name='assignment_detail'),
     path('assignment/<int:pk>/submit/', views.submit_work, name='submit_work'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

    
    path('view_assignments/', views.view_assignments, name='view_assignments'),

    # Password reset URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]
