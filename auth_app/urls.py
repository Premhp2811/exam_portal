from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Student login (OTP)
    path('student-login/', views.student_login, name='student_login'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    
    # Teacher login (Username/Password)
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('teacher-login-submit/', views.teacher_login_submit, name='teacher_login_submit'),
    
    # Branch/Year/Semester selection
    path('select-branch/', views.select_branch, name='select_branch'),
    path('select-year/<str:branch>/', views.select_year, name='select_year'),
    path('select-semester/<str:branch>/<str:year>/', views.select_semester, name='select_semester'),
    path('view-papers/<str:branch>/<str:year>/<str:semester>/', views.view_papers, name='view_papers'),
    path('select-branch/', views.select_branch, name='select_branch'),
    path('select-year/<str:branch>/', views.select_year, name='select_year'),
    path('select-semester/<str:branch>/<str:year>/', views.select_semester, name='select_semester'),
    path('view-papers/<str:branch>/<str:year>/<str:semester>/', views.view_papers, name='view_papers'),
    path('view-syllabus/<str:branch>/', views.view_syllabus, name='view_syllabus'),
    # Teacher upload functionality
    path('teacher/upload/', views.teacher_upload, name='teacher_upload'),
    path('teacher/upload/<str:year>/', views.teacher_select_semester, name='teacher_select_semester'),
    path('teacher/upload/<str:year>/<str:semester>/', views.teacher_upload_form, name='teacher_upload_form'),
    path('teacher/upload/', views.teacher_upload, name='teacher_upload'),
    path('teacher/upload/<str:year>/', views.teacher_select_semester, name='teacher_select_semester'),
    path('teacher/upload/<str:year>/<str:semester>/', views.teacher_upload_form, name='teacher_upload_form'),
    path('teacher/upload-syllabus/', views.teacher_upload_syllabus, name='teacher_upload_syllabus'),
    path('teacher/upload/', views.teacher_upload, name='teacher_upload'),
    path('teacher/upload/<str:year>/', views.teacher_select_semester, name='teacher_select_semester'),
    path('teacher/upload/<str:year>/<str:semester>/', views.teacher_upload_form, name='teacher_upload_form'),
    path('teacher/upload-syllabus/', views.teacher_upload_syllabus, name='teacher_upload_syllabus'),
    path('teacher/manage-papers/', views.teacher_manage_papers, name='teacher_manage_papers'),
    path('teacher/delete-paper/<int:paper_id>/', views.delete_paper, name='delete_paper'),
    path('teacher/delete-syllabus/<int:syllabus_id>/', views.delete_syllabus, name='delete_syllabus'),
    
    
    # Dashboard and logout
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
]