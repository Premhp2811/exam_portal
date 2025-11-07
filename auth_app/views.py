from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
import random
import datetime
from .models import ExamPaper
from django.core.files.storage import FileSystemStorage
import os
from .models import ExamPaper, Syllabus
# Store OTPs temporarily (in production, use database or Redis)
otp_storage = {}

# Teacher credentials (hardcoded - in production, use database)
# Teacher credentials with branch assignment (hardcoded - in production, use database)
TEACHER_CREDENTIALS = {
    'krishna': {'password': '1234', 'branch': 'ist', 'name': 'Krishna'},
    'rajesh': {'password': 'raj123', 'branch': 'cse', 'name': 'Rajesh Kumar'},
    'priya': {'password': 'priya456', 'branch': 'ece', 'name': 'Priya Sharma'},
    'suresh': {'password': 'sure789', 'branch': 'mech', 'name': 'Suresh Patel'},
    'anita': {'password': 'anita321', 'branch': 'civil', 'name': 'Anita Singh'},
    'vijay': {'password': 'vijay999', 'branch': 'eee', 'name': 'Vijay Reddy'},
    'meena': {'password': 'meena555', 'branch': 'auto', 'name': 'Meena Das'},
    'arun': {'password': 'arun777', 'branch': 'ice', 'name': 'Arun Verma'},
}

# Branch mapping
BRANCHES = {
    'cse': 'Computer Science & Engineering',
    'civil': 'Civil Engineering',
    'auto': 'Automobile Engineering',
    'eee': 'Electrical & Electronics Engineering',
    'ece': 'Electronics & Communication Engineering',
    'ist': 'Information Science & Technology',
    'ice': 'Instrumentation & Control Engineering',
    'mech': 'Mechanical Engineering',
}

# Year mapping
YEARS = {
    'first': 'First Year',
    'second': 'Second Year',
    'third': 'Third Year',
}

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

# ============== HOME PAGE ==============
def home(request):
    """Display home page with user type selection"""
    return render(request, 'home.html')

# ============== STUDENT LOGIN (OTP) ==============
def student_login(request):
    """Display the student login page"""
    return render(request, 'login.html')

def send_otp(request):
    """Send OTP to student's email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Please enter your email address')
            return render(request, 'login.html')
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP with timestamp (expires in 5 minutes)
        otp_storage[email] = {
            'otp': otp,
            'timestamp': datetime.datetime.now()
        }
        
        # Send email
        try:
            subject = 'Your OTP for Exam Papers Portal'
            message = f'Your One-Time Password (OTP) is: {otp}\n\nThis OTP will expire in 5 minutes.\n\nIf you did not request this, please ignore this email.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list)
            
            messages.success(request, f'OTP sent successfully to {email}')
            return render(request, 'verify_otp.html', {'email': email})
            
        except Exception as e:
            messages.error(request, f'Failed to send OTP. Error: {str(e)}')
            return render(request, 'login.html')
    
    return redirect('student_login')

def verify_otp(request):
    """Verify the OTP entered by student"""
    if request.method == 'POST':
        email = request.POST.get('email')
        entered_otp = request.POST.get('otp')
        
        if email not in otp_storage:
            messages.error(request, 'OTP expired or invalid. Please request a new one.')
            return redirect('student_login')
        
        stored_data = otp_storage[email]
        stored_otp = stored_data['otp']
        timestamp = stored_data['timestamp']
        
        # Check if OTP is expired (5 minutes)
        time_diff = datetime.datetime.now() - timestamp
        if time_diff.total_seconds() > 300:  # 5 minutes
            del otp_storage[email]
            messages.error(request, 'OTP expired. Please request a new one.')
            return redirect('student_login')
        
        # Verify OTP
        if entered_otp == stored_otp:
            # OTP is correct - clear it from storage
            del otp_storage[email]
            
            # Store email and user type in session
            request.session['user_email'] = email
            request.session['user_type'] = 'student'
            
            messages.success(request, 'Login successful!')
            return redirect('select_branch')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'verify_otp.html', {'email': email})
    
    return redirect('student_login')

# ============== TEACHER LOGIN (Username/Password) ==============
def teacher_login(request):
    """Display the teacher login page"""
    return render(request, 'teacher_login.html')

def teacher_login_submit(request):
    """Handle teacher login submission"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Verify credentials
        if username in TEACHER_CREDENTIALS:
            teacher_data = TEACHER_CREDENTIALS[username]
            if teacher_data['password'] == password:
                # Login successful
                request.session['user_email'] = username
                request.session['user_type'] = 'teacher'
                request.session['teacher_name'] = teacher_data['name']
                request.session['teacher_branch'] = teacher_data['branch']
                
                messages.success(request, f'Welcome, {teacher_data["name"]}!')
                return redirect('teacher_dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
        
        return render(request, 'teacher_login.html')
    
    return redirect('teacher_login')

# ============== BRANCH/YEAR/SEMESTER SELECTION ==============
def select_branch(request):
    """Display branch selection page"""
    if 'user_email' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('home')
    
    email = request.session.get('user_email')
    return render(request, 'select_branch.html', {'email': email})

def select_year(request, branch):
    """Display year selection page"""
    if 'user_email' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('home')
    
    if branch not in BRANCHES:
        messages.error(request, 'Invalid branch selected')
        return redirect('select_branch')
    
    email = request.session.get('user_email')
    branch_name = BRANCHES[branch]
    
    return render(request, 'select_year.html', {
        'email': email,
        'branch': branch,
        'branch_name': branch_name
    })

def select_semester(request, branch, year):
    """Display semester selection page"""
    if 'user_email' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('home')
    
    if branch not in BRANCHES or year not in YEARS:
        messages.error(request, 'Invalid selection')
        return redirect('select_branch')
    
    email = request.session.get('user_email')
    branch_name = BRANCHES[branch]
    year_name = YEARS[year]
    
    return render(request, 'select_semester.html', {
        'email': email,
        'branch': branch,
        'branch_name': branch_name,
        'year': year,
        'year_name': year_name
    })

def view_papers(request, branch, year, semester):
    """Display exam papers for selected branch/year/semester"""
    if 'user_email' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('home')
    
    if branch not in BRANCHES or year not in YEARS:
        messages.error(request, 'Invalid selection')
        return redirect('select_branch')
    
    email = request.session.get('user_email')
    branch_name = BRANCHES[branch]
    year_name = YEARS[year]
    
    # Fetch papers from database - separate by type
    internal_papers = ExamPaper.objects.filter(
        branch=branch,
        year=year,
        semester=semester,
        paper_type='Internal'
    ).order_by('-uploaded_at')
    
    semend_papers = ExamPaper.objects.filter(
        branch=branch,
        year=year,
        semester=semester,
        paper_type='Sem End'
    ).order_by('-uploaded_at')
    
    model_papers = ExamPaper.objects.filter(
        branch=branch,
        year=year,
        semester=semester,
        paper_type='Model'
    ).order_by('-uploaded_at')
    
    return render(request, 'view_papers.html', {
        'email': email,
        'branch': branch,
        'branch_name': branch_name,
        'year': year,
        'year_name': year_name,
        'semester': semester,
        'internal_papers': internal_papers,
        'semend_papers': semend_papers,
        'model_papers': model_papers,
    })
# ============== TEACHER DASHBOARD ==============
def teacher_dashboard(request):
    """Teacher dashboard page after successful login"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    teacher_name = request.session.get('teacher_name', 'Teacher')
    branch_code = request.session.get('teacher_branch', 'cse')
    branch_name = BRANCHES.get(branch_code, 'Unknown Branch')
    
    return render(request, 'teacher_dashboard.html', {
        'teacher_name': teacher_name,
        'branch': branch_code,
        'branch_name': branch_name
    })
# ============== DASHBOARD ==============
def dashboard(request):
    """Dashboard page after successful login"""
    if 'user_email' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('home')
    
    email = request.session.get('user_email')
    user_type = request.session.get('user_type', 'student')
    
    return render(request, 'dashboard.html', {
        'email': email,
        'user_type': user_type
    })

# ============== TEACHER UPLOAD FUNCTIONALITY ==============
def teacher_upload(request):
    """Teacher upload page - select year"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    teacher_name = request.session.get('teacher_name', 'Teacher')
    branch_code = request.session.get('teacher_branch', 'cse')
    branch_name = BRANCHES.get(branch_code, 'Unknown Branch')
    
    return render(request, 'teacher_upload.html', {
        'teacher_name': teacher_name,
        'branch': branch_code,
        'branch_name': branch_name
    })

def teacher_select_semester(request, year):
    """Teacher select semester for upload"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    if year not in YEARS:
        messages.error(request, 'Invalid year selected')
        return redirect('teacher_upload')
    
    teacher_name = request.session.get('teacher_name', 'Teacher')
    branch_code = request.session.get('teacher_branch', 'cse')
    branch_name = BRANCHES.get(branch_code, 'Unknown Branch')
    year_name = YEARS[year]
    
    return render(request, 'teacher_select_semester.html', {
        'teacher_name': teacher_name,
        'branch': branch_code,
        'branch_name': branch_name,
        'year': year,
        'year_name': year_name
    })

def teacher_upload_form(request, year, semester):
    """Teacher upload form and handle submission"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    teacher_name = request.session.get('teacher_name', 'Teacher')
    branch_code = request.session.get('teacher_branch', 'cse')
    branch_name = BRANCHES.get(branch_code, 'Unknown Branch')
    year_name = YEARS.get(year, 'Unknown Year')
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        paper_type = request.POST.get('paper_type')
        year_exam = request.POST.get('year_exam')
        description = request.POST.get('description', '')
        uploaded_file = request.FILES.get('file')
        
        # Validation
        if not all([subject, paper_type, year_exam, uploaded_file]):
            messages.error(request, 'Please fill all required fields')
            return render(request, 'teacher_upload_form.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name,
                'year': year,
                'year_name': year_name,
                'semester': semester
            })
        
        # Check file type
        if not uploaded_file.name.endswith('.pdf'):
            messages.error(request, 'Only PDF files are allowed')
            return render(request, 'teacher_upload_form.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name,
                'year': year,
                'year_name': year_name,
                'semester': semester
            })
        
        # Check file size (10MB max)
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size should not exceed 10MB')
            return render(request, 'teacher_upload_form.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name,
                'year': year,
                'year_name': year_name,
                'semester': semester
            })
        
        # Save to database
        try:
            exam_paper = ExamPaper(
                branch=branch_code,
                year=year,
                semester=semester,
                subject=subject,
                paper_type=paper_type,
                year_exam=year_exam,
                description=description,
                file=uploaded_file,
                uploaded_by=teacher_name
            )
            exam_paper.save()
            
            messages.success(request, f'Paper uploaded successfully! Students can now access it.')
            return redirect('teacher_dashboard')
            
        except Exception as e:
            messages.error(request, f'Failed to upload paper: {str(e)}')
    
    return render(request, 'teacher_upload_form.html', {
        'teacher_name': teacher_name,
        'branch': branch_code,
        'branch_name': branch_name,
        'year': year,
        'year_name': year_name,
        'semester': semester
    })
# ============== SYLLABUS FUNCTIONALITY ==============
def teacher_upload_syllabus(request):
    """Teacher upload syllabus"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    teacher_name = request.session.get('teacher_name', 'Teacher')
    branch_code = request.session.get('teacher_branch', 'cse')
    branch_name = BRANCHES.get(branch_code, 'Unknown Branch')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        academic_year = request.POST.get('academic_year')
        description = request.POST.get('description', '')
        uploaded_file = request.FILES.get('file')
        
        # Validation
        if not all([title, academic_year, uploaded_file]):
            messages.error(request, 'Please fill all required fields')
            return render(request, 'teacher_upload_syllabus.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name
            })
        
        # Check file type
        if not uploaded_file.name.endswith('.pdf'):
            messages.error(request, 'Only PDF files are allowed')
            return render(request, 'teacher_upload_syllabus.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name
            })
        
        # Check file size (10MB max)
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size should not exceed 10MB')
            return render(request, 'teacher_upload_syllabus.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name
            })
        
        # Save to database
        try:
            syllabus = Syllabus(
                branch=branch_code,
                title=title,
                academic_year=academic_year,
                description=description,
                file=uploaded_file,
                uploaded_by=teacher_name
            )
            syllabus.save()
            
            messages.success(request, f'Syllabus uploaded successfully!')
            return redirect('teacher_dashboard')
            
        except Exception as e:
            messages.error(request, f'Failed to upload syllabus: {str(e)}')
    
    return render(request, 'teacher_upload_syllabus.html', {
        'teacher_name': teacher_name,
        'branch': branch_code,
        'branch_name': branch_name
    })

def view_syllabus(request, branch):
    """Student view syllabus for their branch"""
    if 'user_email' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('home')
    
    if branch not in BRANCHES:
        messages.error(request, 'Invalid branch selected')
        return redirect('select_branch')
    
    email = request.session.get('user_email')
    branch_name = BRANCHES[branch]
    
    # Fetch syllabus from database
    syllabus_list = Syllabus.objects.filter(branch=branch).order_by('-uploaded_at')
    
    return render(request, 'view_syllabus.html', {
        'email': email,
        'branch': branch,
        'branch_name': branch_name,
        'syllabus_list': syllabus_list
    })
# ============== MANAGE PAPERS FUNCTIONALITY ==============
def teacher_manage_papers(request):
    """Teacher manage/delete papers and syllabus"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    teacher_name = request.session.get('teacher_name', 'Teacher')
    branch_code = request.session.get('teacher_branch', 'cse')
    branch_name = BRANCHES.get(branch_code, 'Unknown Branch')
    
    # Get all uploads by this teacher
    syllabus_list = Syllabus.objects.filter(
        branch=branch_code,
        uploaded_by=teacher_name
    ).order_by('-uploaded_at')
    
    internal_papers = ExamPaper.objects.filter(
        branch=branch_code,
        uploaded_by=teacher_name,
        paper_type='Internal'
    ).order_by('-uploaded_at')
    
    semend_papers = ExamPaper.objects.filter(
        branch=branch_code,
        uploaded_by=teacher_name,
        paper_type='Sem End'
    ).order_by('-uploaded_at')
    
    model_papers = ExamPaper.objects.filter(
        branch=branch_code,
        uploaded_by=teacher_name,
        paper_type='Model'
    ).order_by('-uploaded_at')
    
    return render(request, 'teacher_manage_papers.html', {
        'teacher_name': teacher_name,
        'branch': branch_code,
        'branch_name': branch_name,
        'syllabus_list': syllabus_list,
        'internal_papers': internal_papers,
        'semend_papers': semend_papers,
        'model_papers': model_papers,
    })

def delete_paper(request, paper_id):
    """Delete exam paper"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    if request.method == 'POST':
        try:
            paper = ExamPaper.objects.get(id=paper_id)
            
            # Check if this teacher uploaded this paper
            teacher_name = request.session.get('teacher_name', 'Teacher')
            if paper.uploaded_by != teacher_name:
                messages.error(request, 'You can only delete your own uploads')
                return redirect('teacher_manage_papers')
            
            # Delete the file from storage
            if paper.file:
                paper.file.delete()
            
            # Delete from database
            paper.delete()
            messages.success(request, 'Paper deleted successfully!')
            
        except ExamPaper.DoesNotExist:
            messages.error(request, 'Paper not found')
        except Exception as e:
            messages.error(request, f'Error deleting paper: {str(e)}')
    
    return redirect('teacher_manage_papers')

def delete_syllabus(request, syllabus_id):
    """Delete syllabus"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    if request.method == 'POST':
        try:
            syllabus = Syllabus.objects.get(id=syllabus_id)
            
            # Check if this teacher uploaded this syllabus
            teacher_name = request.session.get('teacher_name', 'Teacher')
            if syllabus.uploaded_by != teacher_name:
                messages.error(request, 'You can only delete your own uploads')
                return redirect('teacher_manage_papers')
            
            # Delete the file from storage
            if syllabus.file:
                syllabus.file.delete()
            
            # Delete from database
            syllabus.delete()
            messages.success(request, 'Syllabus deleted successfully!')
            
        except Syllabus.DoesNotExist:
            messages.error(request, 'Syllabus not found')
        except Exception as e:
            messages.error(request, f'Error deleting syllabus: {str(e)}')
    
    return redirect('teacher_manage_papers')
# ============== SYLLABUS FUNCTIONALITY ==============
def teacher_upload_syllabus(request):
    """Teacher upload syllabus"""
    if 'user_email' not in request.session or request.session.get('user_type') != 'teacher':
        messages.error(request, 'Please login as teacher first')
        return redirect('teacher_login')
    
    teacher_name = request.session.get('teacher_name', 'Teacher')
    branch_code = request.session.get('teacher_branch', 'cse')
    branch_name = BRANCHES.get(branch_code, 'Unknown Branch')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        academic_year = request.POST.get('academic_year')
        description = request.POST.get('description', '')
        uploaded_file = request.FILES.get('file')
        
        # Validation
        if not all([title, academic_year, uploaded_file]):
            messages.error(request, 'Please fill all required fields')
            return render(request, 'teacher_upload_syllabus.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name
            })
        
        # Check file type
        if not uploaded_file.name.endswith('.pdf'):
            messages.error(request, 'Only PDF files are allowed')
            return render(request, 'teacher_upload_syllabus.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name
            })
        
        # Check file size (10MB max)
        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size should not exceed 10MB')
            return render(request, 'teacher_upload_syllabus.html', {
                'teacher_name': teacher_name,
                'branch': branch_code,
                'branch_name': branch_name
            })
        
        # Save to database
        try:
            syllabus = Syllabus(
                branch=branch_code,
                title=title,
                academic_year=academic_year,
                description=description,
                file=uploaded_file,
                uploaded_by=teacher_name
            )
            syllabus.save()
            
            messages.success(request, f'Syllabus uploaded successfully!')
            return redirect('teacher_dashboard')
            
        except Exception as e:
            messages.error(request, f'Failed to upload syllabus: {str(e)}')
    
    return render(request, 'teacher_upload_syllabus.html', {
        'teacher_name': teacher_name,
        'branch': branch_code,
        'branch_name': branch_name
    })

def view_syllabus(request, branch):
    """Student view syllabus for their branch"""
    if 'user_email' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('home')
    
    if branch not in BRANCHES:
        messages.error(request, 'Invalid branch selected')
        return redirect('select_branch')
    
    email = request.session.get('user_email')
    branch_name = BRANCHES[branch]
    
    # Fetch syllabus from database
    syllabus_list = Syllabus.objects.filter(branch=branch).order_by('-uploaded_at')
    
    return render(request, 'view_syllabus.html', {
        'email': email,
        'branch': branch,
        'branch_name': branch_name,
        'syllabus_list': syllabus_list
    })
# ============== LOGOUT ==============
def logout(request):
    """Logout user"""
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('home')