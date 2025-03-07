from django.shortcuts import render,redirect,get_object_or_404
from .models import Notices,Timetable,Teacher,Subject,Student,Attendance,TeacherSubjectAssignment,Department,Year,Classes,ClassTeacherAssignment
from supabase import create_client, Client,SupabaseAuthClient
from django.core.serializers import serialize
from django.shortcuts import render
from erp_1.decorators import supabase_login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F, FloatField, Case, When
from .models import Teacher, ClassTeacherAssignment, Student, Attendance,Slots,LeaveRequest,LeaveType,TempTimetable
from datetime import datetime, date, timedelta  # Update this import line
from django.utils import timezone
from django.http import JsonResponse
from django.db import DatabaseError
from collections import defaultdict
from django.db.models import Case, When, IntegerField
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Notices
import supabase
import logging
from django.conf import settings
logger = logging.getLogger(__name__)

@supabase_login_required
def index(request):
    try:
        email = request.session.get('teacher_email')
        if not email:
            return render(request, 'error.html', {
                'error_title': 'Session Expired',
                'error_message': 'Please log in again to continue.',
                'return_url': 'login',
                'return_text': 'Login Page'
            })

        today = date.today()
        timefrom = "09:15 am"
        timeto = "10:15 am"
        today_date = date.today()
        day_name = today_date.strftime("%A")
        # Optimize teacher query with select_related
        try:
            teacher = (
                Teacher.objects.select_related('RoleID', 'DepartmentID')
                .get(Email=email)
            )
        except Teacher.DoesNotExist:
            return render(request, 'error.html', {
                'error_title': 'User Not Found',
                'error_message': 'Teacher account not found.',
                'return_url': 'login',
                'return_text': 'Login Page'
            })

        role = teacher.RoleID.RoleName

        if role == 'Teacher' or role == 'HOD':
            try:
                # Add ordering to the aggregation query
                attendance_data = (
                    Attendance.objects.filter(
                        ClassID__DepartmentID=teacher.DepartmentID,
                        Date=today
                    ).filter(
                        Q(Timefrom=timefrom, Timeto=timeto) |
                        Q(Timefrom=timefrom, Timeto='11:15 am')
                    ).values('ClassID__DepartmentID')
                    .annotate(
                        present_count=Count('Status', filter=Q(Status=True)),
                        absent_count=Count('Status', filter=Q(Status=False))
                    ).order_by('ClassID__DepartmentID')  # Add ordering
                    .first()
                )

                total_count = Student.objects.filter(
                    CurrentClassID__DepartmentID=teacher.DepartmentID
                ).count()
                employeesOnLeave = LeaveRequest.objects.filter(
                    Q(StartDate__lte=today) & Q(EndDate__gte=today),
                    Status='Approved',
                    TeacherID__DepartmentID=teacher.DepartmentID
                )
                todays_classes1 = TempTimetable.objects.filter(Date=today)
                todaysclases2 = Timetable.objects.filter(Day=day_name,SubjectAssignmentID__TeacherID=teacher.Teacherid)
                present_count = attendance_data['present_count'] if attendance_data else 0
                absent_count = attendance_data['absent_count'] if attendance_data else 0
                attendance_percentage = (present_count / total_count * 100) if total_count > 0 else 0
                
            except DatabaseError as e:
                logger.error(f'Database error in index view: {str(e)}')
                return render(request, 'error.html', {
                    'error_title': 'Database Error',
                    'error_message': 'Unable to fetch attendance data.',
                    'error_details': str(e) if settings.DEBUG else None,
                    'return_url': '/',
                    'return_text': 'Try Again'
                })

        elif role == 'Principal':
            try:
                # Add ordering to the principal's aggregation query
                attendance_data = (
                    Attendance.objects.filter(
                        Date=today
                    ).filter(
                        Q(Timefrom=timefrom, Timeto=timeto) |
                        Q(Timefrom=timefrom, Timeto='11:15 am')
                    ).values('ClassID__DepartmentID')
                    .annotate(
                        present_count=Count('Status', filter=Q(Status=True)),
                        absent_count=Count('Status', filter=Q(Status=False))
                    ).order_by('ClassID__DepartmentID')  # Add ordering
                    .first()
                )
                employeesOnLeave = LeaveRequest.objects.filter(
                    Q(StartDate__lte=today) & Q(EndDate__gte=today),
                    Status='Approved'
                )
                todays_classes1 = TempTimetable.objects.filter(Date=today)
                todaysclases2 = Timetable.objects.filter(Day=day_name)
                total_count = Student.objects.count()
                present_count = attendance_data['present_count'] if attendance_data else 0
                absent_count = attendance_data['absent_count'] if attendance_data else 0
                attendance_percentage = (present_count / total_count * 100) if total_count > 0 else 0

            except DatabaseError as e:
                logger.error(f'Database error in index view: {str(e)}')
                return render(request, 'error.html', {
                    'error_title': 'Database Error',
                    'error_message': 'Unable to fetch attendance data.',
                    'error_details': str(e) if settings.DEBUG else None,
                    'return_url': '/',
                    'return_text': 'Try Again'
                })
        else:
            # For other roles, just show basic interface
            return render(request, 'index.html', {'teacher': teacher})
            
        context = {
            'teacher': teacher,
            'present': present_count,
            'absent': absent_count,
            'total': total_count,
            'employeesOnLeave': employeesOnLeave,
            'attendance_percentage': attendance_percentage,
            'todays_classes1': todays_classes1,
            'todaysclases2': todaysclases2,
        }
        print(todaysclases2)
        return render(request, 'index.html', context)

    except Exception as e:
        logger.error(f'Unexpected error in index view: {str(e)}')
        return render(request, 'error.html', {
            'error_title': 'System Error',
            'error_message': 'An unexpected error occurred.',
            'error_details': str(e) if settings.DEBUG else None,
            'return_url': '/',
            'return_text': 'Home'
        })


def login(request):
    if request.method == 'POST':
        url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
        key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
        supabase: Client = create_client(url, key)
        
        email = request.POST.get('username1', '').strip()
        password = request.POST.get('password', '')

        try:
            response = supabase.auth.sign_in_with_password({'email': email, 'password': password})
            user = response.user

            if user:
                request.session['teacher_email'] = email
                return redirect('/')
                 # Redirect to the index page after login

        except Exception as e:
            # Handle authentication error
            error_message = "Invalid login credentials. Please try again."
            print(e)  # Print the error for debugging
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def logout(request):
    url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
    supabase: Client = create_client(url, key)

    try:
        res = supabase.auth.sign_out()
    except Exception as e:
        print(e)
    
    request.session.flush()
    return redirect('login/')


import csv
from django.http import HttpResponse

def download_csv_template(request):
    # Define the CSV format headers
    csv_header = [
        'rollnumber',
        'firstname', 'lastname','batch', 'email', 
        'mobile_number', 'PRN', 
        'classid'
    ]
    
    # Create the HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_template.csv"'

    # Write CSV header to the response
    writer = csv.writer(response)
    writer.writerow(csv_header)
    
    return response

@supabase_login_required
def student(request):
    if request.method == 'POST':
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return render(request, 'student_form.html')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
                key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
                supabase: Client = create_client(url, key)
                res = supabase.auth.sign_out()
                
                for row in reader:
                    firstname = row['firstname']
                    lastname = row['lastname']
                    email = row['email']
                    password = '123456'  
                    mobile_number = row['mobile_number']
                    RollNumber=row['rollnumber']
                    classid=row['classid']
                    
                    try:
                        sign_up_response = supabase.auth.sign_up({
                            'email': email,
                            'password': password,
                        })
                        current_class = get_object_or_404(Classes, pk=classid)
                        # Check if the sign-up was successful
                        if sign_up_response.user:
                            user_id = sign_up_response.user.id  # Get the user ID (UUID)

                            # Create a Student instance in the database
                            Student.objects.create(
                                StudentID=user_id,
                                FirstName=firstname,
                                Email=email,
                                LastName=lastname,
                                MobileNumber=mobile_number,
                                RollNumber=RollNumber,
                                CurrentClassID=current_class
                            )

                    except Exception as e:
                        error_message = str(e)
                        print(f"Error processing row {row}: {error_message}")
                        continue  # Skip to the next row if there's an error

                messages.success(request, 'Students registered successfully.')
                return redirect('student')  # Redirect to a success page

            except Exception as e:
                error_message = str(e)
                print("Error processing CSV file:", error_message)
                messages.error(request, 'There was an error processing the CSV file.')
                return render(request, 'student_form.html')

        else:
            messages.error(request, 'No CSV file uploaded.')
            return render(request, 'student_form.html')

    return render(request, 'student_form.html')

@supabase_login_required
def students(request):
    try:
        # Get teacher info with prefetch
        email = request.session.get('teacher_email')
        teacher = get_object_or_404(Teacher.objects.select_related('RoleID', 'DepartmentID'), Email=email)
        
        # Fetch all years and departments in single query
        year_list = Year.objects.all().order_by('YearID')
        department_list = Department.objects.all().order_by('DepartmentName')
        
        if request.method == 'POST':
            yearid = request.POST.get('year')
            departmentid = request.POST.get('department')
            
            # Get class info with a single optimized query
            current_class = get_object_or_404(
                Classes.objects.select_related('DepartmentID', 'YearID'),
                DepartmentID=departmentid, 
                YearID=yearid
            )

            # Optimize student query with select_related
            students = Student.objects.filter(
                CurrentClassID=current_class.ClassID
            ).select_related('CurrentClassID').order_by('RollNumber')

            if not students.exists():
                messages.warning(request, 'No students found in this class.')
                return render(request, 'students.html', {
                    'year': year_list,
                    'department': department_list,
                    'teacher': teacher
                })



            context = {
                'year': year_list,
                'department': department_list,
                'students_data': students,
                'teacher': teacher,
                'selected_year': yearid,
                'selected_department': departmentid,
                'current_class': current_class
            }

            return render(request, 'students.html', context)

        return render(request, 'students.html', {
            'year': year_list,
            'department': department_list,
            'teacher': teacher
        })

    except Exception as e:
        logger.error(f'Error in students view: {str(e)}')
        messages.error(request, 'An error occurred while fetching student data')
        return redirect('erp_1:index')

@supabase_login_required
def custom_report(request):
    try:
        email = request.session.get('teacher_email')
        teacher = get_object_or_404(Teacher.objects.select_related('RoleID', 'DepartmentID'), Email=email)
        role = teacher.RoleID.RoleName
        
        # Handle departments based on role
        if role == 'HOD':
            departments = [teacher.DepartmentID]
            selected_department = teacher.DepartmentID.DepartmentID
        elif role == 'Principal':
            departments = Department.objects.all()
            selected_department = request.GET.get('department')
        else:  # Regular teacher
            # Get departments from teacher's assigned subjects
            assigned_dept_ids = TeacherSubjectAssignment.objects.filter(
                TeacherID=teacher
            ).values_list('SubjectID__CurrentClassID__DepartmentID', flat=True).distinct()
            departments = Department.objects.filter(DepartmentID__in=assigned_dept_ids)
            selected_department = request.GET.get('department')

        # Get classes based on department and role
        if selected_department:
            if role == 'Teacher':
                # Filter classes by teacher's assignments
                class_ids = TeacherSubjectAssignment.objects.filter(
                    TeacherID=teacher,
                    SubjectID__CurrentClassID__DepartmentID=selected_department
                ).values_list('SubjectID__CurrentClassID', flat=True).distinct()
                classes = Classes.objects.filter(ClassID__in=class_ids)
            else:
                classes = Classes.objects.filter(DepartmentID=selected_department)
        else:
            classes = Classes.objects.none()

        # Get subjects and handle selected class
        selected_class = request.GET.get('class')
        subjects = []
        if selected_class:
            if role == 'Teacher':
                subjects = Subject.objects.filter(
                    teachersubjectassignment__TeacherID=teacher,
                    CurrentClassID=selected_class
                ).distinct()
            else:
                subjects = Subject.objects.filter(CurrentClassID=selected_class)

        selected_subject = request.GET.get('subject')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        attendance_data = []
        if all([selected_class, selected_subject, start_date, end_date]):
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                
                # Get students and their attendance records
                students = Student.objects.filter(
                    CurrentClassID=selected_class
                ).order_by('RollNumber')

                # Optimize attendance query with annotations
                attendance_records = (
                    Attendance.objects.filter(
                        StudentID__in=students.values_list('StudentID', flat=True),
                        SubjectID=selected_subject,
                        Date__range=(start_date, end_date)
                    ).values('StudentID')
                    .annotate(
                        attended_count=Count('AttendanceID', filter=Q(Status=True)),
                        total_lectures=Count('AttendanceID'),
                        attendance_percentage=Case(
                            When(total_lectures__gt=0, 
                                 then=100.0 * Count('AttendanceID', filter=Q(Status=True)) / Count('AttendanceID')),
                            default=0.0,
                            output_field=FloatField(),
                        )
                    )
                )

                # Create lookup dictionary for O(1) access
                attendance_lookup = {
                    record['StudentID']: record for record in attendance_records
                }

                # Prepare attendance data
                for student in students:
                    record = attendance_lookup.get(student.StudentID, {
                        'attended_count': 0,
                        'total_lectures': 0,
                        'attendance_percentage': 0
                    })

                    attendance_data.append({
                        'student': {
                            'RollNo': student.RollNumber,
                            'FirstName': student.FirstName,
                            'LastName': student.LastName,
                        },
                        'attendance': [{
                            'attended_count': record['attended_count'],
                            'total_lectures': record['total_lectures']
                        }],
                        'total_attended': record['attended_count'],
                        'average_percentage': record['attendance_percentage']
                    })

            except ValueError as e:
                messages.error(request, 'Invalid date format')
                logger.error(f'Date parsing error in custom_report: {str(e)}')
                return render(request, 'attendance_report.html', {
                    'teacher': teacher,
                    'departments': departments,
                    'classes': classes,
                    'subjects': subjects,
                })

        context = {
            'teacher': teacher,
            'departments': departments,
            'classes': classes,
            'subjects': subjects,
            'selected_department': selected_department,
            'selected_class': selected_class,
            'selected_subject': selected_subject,
            'attendance_data': attendance_data,
            'start_date': start_date if 'start_date' in locals() else None,
            'end_date': end_date if 'end_date' in locals() else None,
        }

        return render(request, 'attendance_report.html', context)

    except Exception as e:
        logger.error(f'Error in custom_report: {str(e)}')
        messages.error(request, 'An error occurred while generating the report')
        return redirect('erp_1:preports')

@supabase_login_required
def notices(request):
    allnotices= Notices.objects.order_by('-date')
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    role=teacher.RoleID.RoleName
    is_teacher = role == 'Teacher' 
    department=teacher.DepartmentID.DepartmentName
    url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
    supabase: Client = create_client(url, key)
    if request.method == 'POST':
            title = request.POST.get('title')
            teacherid=teacher.Teacherid
            date = request.POST.get('date')
            classid=request.POST.get('class')
            classid=Classes.objects.get(ClassID=classid)
            attachment = request.POST.get('file')
            print(attachment)
            notice = Notices.objects.create(
            title=title,
            teacherpublished=teacher,
            ClassID=classid,
            date=date,
            attachment=attachment,
        )
            return redirect('notices')
    allnotices=Notices.objects.filter(ClassID__DepartmentID=teacher.DepartmentID).order_by('-date')
    classes=Classes.objects.filter(DepartmentID__DepartmentName=department)
    return render(request, 'notices.html',{'notice': allnotices,'teacher':teacher,'classes':classes})




@supabase_login_required
def delete_notice(request, id):
    if request.method == 'POST':
        # Initialize Supabase client
        supabase_url = 'https://gipdgkwmxmmykyaliwhr.supabase.co/'
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
                
        supabase_client = supabase.create_client(supabase_url, supabase_key)
        
        # Get the notice object
        notice = Notices.objects.get(id=id)
        class_id = notice.ClassID.ClassID
        attachment = notice.attachment
        
        # Delete the notice record from the database
        notice.delete()
        return redirect('notices')
    else:
        return redirect('notices')  # or wherever you want to redirect to

@supabase_login_required
def logs(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)

    today = timezone.now().date()

    # Get start and end dates from the POST request
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')

    # Default dates to today if not provided
    start_date = today if not start_date_str else timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = today if not end_date_str else timezone.datetime.strptime(end_date_str, "%Y-%m-%d").date()

    selected_subject = request.POST.get('subject')

    classteacher = False
    class_id = None

    if teacher.RoleID.RoleName == 'Teacher':
        role = ClassTeacherAssignment.objects.filter(TeacherID=teacher.Teacherid).first()
        if role and role.RoleID.RoleName == 'Classteacher':
            classteacher = True
            class_id = role.ClassID.ClassID  # Get the class ID assigned to the class teacher

    # Get subjects only if the teacher is a class teacher
    subjects = []
    if classteacher:
        subjects = Subject.objects.filter(
            CurrentClassID=class_id  # Only show subjects for the assigned class
        ).order_by('SubjectName')

    # Base query for attendance records within the date range
    attendance_records = Attendance.objects.select_related('SubjectID', 'ClassID').filter(
        Date__range=(start_date, end_date)
    )

    if classteacher:
        # Ensure that the attendance records are filtered by the specific class ID assigned to the teacher
        attendance_records = attendance_records.filter(ClassID=class_id)

        if selected_subject:
            # Further filter by specific subject if selected
            attendance_records = attendance_records.filter(SubjectID=selected_subject)

    elif teacher.RoleID.RoleName == 'Principal':
        # For principals, no further filtering needed
        attendance_records = attendance_records.all()

    else:
        # For other roles, filter attendance records by subjects assigned to the teacher
        assigned_subjects = Subject.objects.filter(
            teachersubjectassignment__TeacherID=teacher
        ).values_list('SubjectID', flat=True)
        attendance_records = attendance_records.filter(
            SubjectID__in=assigned_subjects
        )

    # Annotate the attendance records with counts
    attendance_records = attendance_records.values(
        'Date',  # Include the Date field here
        'Timefrom',
        'Timeto',
        'SubjectID__SubjectName',
        'ClassID__ClassName',  # Assuming you have a ClassName field in Classes
        'SubjectID__SubjectDepartment',
        'SubjectID__SubjectYear',
        'SubjectID__teachersubjectassignment__TeacherID__FirstName'
    ).annotate(
        student_count=Count('StudentID'),
        present_count=Count('StudentID', filter=Q(Status=True)),
        absent_count=Count('StudentID', filter=Q(Status=False))
    ).order_by('Date', 'Timefrom', 'Timeto')

    context = {
        'attendance_records': attendance_records,
        'teacher': teacher,
        'start_date': start_date,
        'end_date': end_date,
        'classteacher': classteacher,
        'selected_subject': selected_subject,
        'subjects': subjects,
    }

    template = 'tlogs.html' if teacher.RoleID.RoleName == 'Teacher' or classteacher else 'logs.html'
    return render(request, template, context)

# @supabase_login_required
# def history(request):
#     return render(request,'history.html')

@supabase_login_required
def preports(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    context={
        'teacher':teacher
    }
    return render(request,'preports.html',context)



@supabase_login_required
def daily_report(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    departments = Department.objects.all()
    if teacher.RoleID.RoleName=='HOD':
        selected_department=teacher.DepartmentID.DepartmentID
    else:
        selected_department = request.GET.get('department')
    
    selected_class = request.GET.get('class')
    if selected_department:
        classes = Classes.objects.filter(DepartmentID=selected_department)
    else:
        classes = Classes.objects.all()

    current_date = timezone.now().date()
    #current_date=current_date-timedelta(1)

    attendance_data = []
    students_in_class = []
    slots=[]
    if selected_class:
        slot_ids = Attendance.objects.filter(Date=current_date,ClassID_id=selected_class).values_list('SlotID', flat=True).distinct()
        slots = Slots.objects.filter(Slotid__in=slot_ids)
        students_in_class = Student.objects.filter(CurrentClassID_id=selected_class).order_by('RollNumber')
        attendance_records = Attendance.objects.filter(Date=current_date, ClassID_id=selected_class)
        # Create a dictionary to track attendance for each slot
        present_students = {}
        for slot in slots:
            slot_key = f"{slot.start_time} - {slot.end_time}"
            present_students[slot_key] = set(attendance_records.filter(SlotID=slot, Status=True).values_list('StudentID', flat=True))

        # Prepare attendance data as a list
        for student in students_in_class:
            student_attendance = {
                'name': f"{student.FirstName} {student.LastName}",
                'roll_number': student.RollNumber,
                'attendance': [],
                'total_attendance': 0
            }
            # Check each slot's attendance
            for slot in slots:
                slot_key = f"{slot.start_time} - {slot.end_time}"
                is_present = student.StudentID in present_students[slot_key]
                student_attendance['attendance'].append(is_present)
                if is_present:
                    student_attendance['total_attendance'] += 1
            attendance_data.append(student_attendance)
    context = {
        'departments': departments,
        'classes': classes,
        'attendance_data': attendance_data,
        'students_in_class': students_in_class,
        'slots': slots,  # Include slots in the context
        'selected_department': selected_department,
        'selected_class': selected_class,
        'teacher':teacher
    }

    return render(request, 'daily_report.html', context)


@supabase_login_required
def weekly_report(request):
    # Get teacher's email from session
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    
    # Get the class or classes based on selection
    departments = Department.objects.all()
    if teacher.RoleID.RoleName == 'HOD':
        selected_department = teacher.DepartmentID.DepartmentID
        print(selected_department)
    else:
        selected_department = request.GET.get('department')
    
    selected_class = request.GET.get('class')
    if selected_department:
        class_obj = Classes.objects.filter(DepartmentID=selected_department)
    else:
        class_obj = Classes.objects.all()

    today = timezone.now().date()
    start_date = today - timedelta(days=today.weekday())  # Adjust to the previous Monday (0 = Monday)

    # Set the end date to the following Friday
    end_date = start_date + timedelta(days=4)
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    attendance_data = []
    
    if selected_class:
        # Convert selected_class to integer for filtering
        selected_class_id = int(selected_class)
        
        # Get attendance records for the selected class
        attendance_records = Attendance.objects.filter(
            Date__range=(start_date, end_date),
            ClassID=selected_class_id
        )

        # Get total students in the class
        total_students = Student.objects.filter(CurrentClassID=selected_class_id).count()

        # Calculate daily aggregates for the graph
        daily_aggregates = []
        for day_offset in range(5):  # Monday to Friday
            current_date = start_date + timedelta(days=day_offset)
            # Count distinct students present on this day
            present_students = (
                attendance_records.filter(Date=current_date, Status=True)
                .values('StudentID')
                .distinct()
                .count()
            )
            
            daily_aggregates.append({
                'date': current_date.strftime('%A'),  # Day name
                'present': present_students,
                'total': total_students
            })

        # Get all students in the class
        students_in_class = Student.objects.filter(CurrentClassID=selected_class_id).order_by('RollNumber')
        
        # Collect attendance data for each student in the class
        attendance_records = Attendance.objects.filter(
            Date__range=(start_date, end_date),
            ClassID=selected_class_id
        )
        
        # Pre-fetch attendance counts per day for each student to minimize DB hits
        attendance_counts = (
            attendance_records
            .values('StudentID', 'Date')
            .annotate(
                attended_count=Count('SlotID', filter=Q(Status=True)),
                conducted_count=Count('SlotID'),
                student_roll=F('StudentID__RollNumber'),
                student_first=F('StudentID__FirstName'),
                student_last=F('StudentID__LastName'),
            ).order_by('student_roll')
        )

        # Prepare data structure with weekly attendance
        for student in students_in_class:
            student_record = {
                'roll_number': student.RollNumber,
                'name': f"{student.FirstName} {student.LastName}",
                'weekly_attendance': [{'attended': 0, 'conducted': 0} for _ in range(5)],  # Only 5 days
                'total_attendance': 0,
            }

            # Map attendance counts for the student for each day
            student_attendance = {
                (entry['Date'], entry['StudentID']): entry
                for entry in attendance_counts
                if entry['StudentID'] == student.StudentID
            }

            # Populate weekly attendance data for each day (only for 5 days)
            for day_offset in range(5):  # Only Monday to Friday
                day_date = start_date + timedelta(days=day_offset)
                day_index = day_offset  # Use day_offset directly as index
            
                # Retrieve attended and conducted count from the pre-fetched data
                daily_data = student_attendance.get((day_date, student.StudentID), {})
                attended = daily_data.get('attended_count', 0)
                conducted = daily_data.get('conducted_count', 0)

                student_record['weekly_attendance'][day_index] = {
                    'attended': attended,
                    'conducted': conducted
                }
                student_record['total_attendance'] += attended

            attendance_data.append(student_record)

    context = {
        'teacher': teacher,
        'attendance_data': attendance_data,
        'selected_department': selected_department,
        'departments': departments,
        'classes': class_obj,
        'day_names': day_names,
        'start_date': start_date,
        'end_date': end_date,
        'selected_class': selected_class,
        'daily_aggregates': daily_aggregates if selected_class else []  # Add daily aggregates to context
    }
    return render(request, 'weekly_report.html', context)

from django.utils import timezone
from datetime import timedelta
@supabase_login_required
def monthly_report(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    departments = Department.objects.all()
    if teacher.RoleID.RoleName == 'HOD':
        selected_department = teacher.DepartmentID.DepartmentID
    else:
        selected_department = request.GET.get('department')
    selected_class = request.GET.get('class')
    classes = Classes.objects.filter(DepartmentID=selected_department) if selected_department else Classes.objects.all()

    attendance_data = []
    subjects_set = set()

    # Get current month's start and end dates
    today = timezone.now().date()
    start_date = today.replace(day=1)  # First day of the current month
    end_date = (today.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # Last day of the month
    current_month = today.strftime("%B")
    # Process attendance for the selected class
    if selected_class:
        students = Student.objects.filter(CurrentClassID_id=selected_class).order_by('RollNumber')

        for student in students:
            # Fetch attendance records for the student within the date range
            student_attendance = Attendance.objects.filter(
                StudentID=student.StudentID,
                Date__range=(start_date, end_date)
            ).values('SubjectID', 'SubjectName').annotate(
                attended_count=Count('AttendanceID', filter=Q(Status=True)),
                total_lectures=Count('Date')
            )

            # Collect subjects and calculate total attended and conducted lectures
            total_attended = 0
            total_conducted = 0

            for record in student_attendance:
                subjects_set.add(record['SubjectName'])
                total_attended += record['attended_count']
                total_conducted += record['total_lectures']

            # Calculate average attendance percentage
            average_percentage = (total_attended / total_conducted) * 100 if total_conducted > 0 else 0

            # Append the student's attendance data
            attendance_data.append({
                'student': {
                    'RollNo': student.RollNumber,
                    'FirstName': student.FirstName,
                    'LastName': student.LastName,
                },
                'attendance': list(student_attendance),
                'total_attended': total_attended,
                'total_conducted': total_conducted,  # Add total conducted lectures
                'average_percentage': average_percentage,
            })

    # Sort subjects for display
    subjects_list = sorted(list(subjects_set))

    # Prepare context for rendering the template
    context = {
        'teacher': teacher,
        'departments': departments,
        'selected_department': selected_department,
        'selected_class': selected_class,
        'classes': classes,
        'current_month':current_month,
        'attendance_data': attendance_data,
        'start_date': start_date,
        'end_date': end_date,
        'subjects_list': subjects_list,  # Include subjects list for the template
    }
    return render(request, 'monthly_report.html', context)


@supabase_login_required
def class_report(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    departments = Department.objects.all()
    if teacher.RoleID.RoleName == 'HOD':
        selected_department = teacher.DepartmentID.DepartmentID
    else:
        selected_department = request.GET.get('department')
    selected_class = request.GET.get('class')
    classes = Classes.objects.filter(DepartmentID=selected_department) if selected_department else Classes.objects.all()
    selected_class = request.GET.get('class')
    students = Student.objects.filter(CurrentClassID=selected_class).order_by('RollNumber')
    attendance_data = []
    subjects_set = set()
    for student in students:
        student_attendance = Attendance.objects.filter(StudentID=student.StudentID).values('SubjectID', 'SubjectName').annotate(
            attended_count=Count('AttendanceID',filter=Q(Status=True)),
            total_lectures=Count('Date')
        )
        for record in student_attendance:
            subjects_set.add(record['SubjectName'])
        total_attended = sum([subject['attended_count'] for subject in student_attendance])
        total_conducted = sum([subject['total_lectures'] for subject in student_attendance])
        average_percentage = (total_attended / total_conducted) * 100 if total_conducted > 0 else 0

        attendance_data.append({
            'student': {
                'RollNo': student.RollNumber,
                'FirstName': student.FirstName,
                'LastName': student.LastName,
            },
            'attendance': list(student_attendance),
            'total_attended': total_attended,
            'average_percentage': average_percentage,
        })
    
    subjects_list = sorted(list(subjects_set))
    
    context = {
        'teacher': teacher,
        'departments':departments,
        'selected_department':selected_department,
        'classes': classes,
        'selected_class': selected_class,
        'attendance_data': attendance_data,
        'subjects': subjects_list,
    }
    return render(request, 'class_report.html', context)

@supabase_login_required
def subjectwise_report(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    departments = Department.objects.all()
    
    # Handle department selection based on role
    if teacher.RoleID.RoleName == 'HOD':
        selected_department = teacher.DepartmentID.DepartmentID
    else:
        selected_department = request.GET.get('department')
    
    # Get classes based on department
    classes = Classes.objects.filter(DepartmentID=selected_department) if selected_department else Classes.objects.all()
    selected_class = request.GET.get('class')
    
    # Get subjects for selected class
    subjects = None
    selected_subject = None
    if selected_class:
        subjects = Subject.objects.filter(CurrentClassID=selected_class)
        selected_subject = request.GET.get('subject')

    report_data = []
    total_lectures = 0
    subject_teacher = None

    if selected_class and selected_subject:
        # Get teacher assigned to this subject
        subject_teacher = TeacherSubjectAssignment.objects.filter(SubjectID=selected_subject).first()
        
        # Get total number of lectures conducted
        total_lectures = Attendance.objects.filter(
            ClassID=selected_class,
            SubjectID=selected_subject
        ).values('Date', 'SlotID').distinct().count()

        # Get attendance data for all students in the class for this subject
        attendance_data = (
            Attendance.objects.filter(
                ClassID=selected_class,
                SubjectID=selected_subject
            )
            .values('StudentID')
            .annotate(
                attended_lectures=Count('AttendanceID', filter=Q(Status=True)),
                total_lectures=Count('AttendanceID'),
                student_roll=F('StudentID__RollNumber'),
                student_first=F('StudentID__FirstName'),
                student_last=F('StudentID__LastName'),
            )
            .order_by('student_roll')
        )

        # Calculate attendance statistics
        for record in attendance_data:
            attendance_percentage = (
                (record['attended_lectures'] / record['total_lectures'] * 100)
                if record['total_lectures'] > 0
                else 0
            )
            report_data.append({
                'student': {
                    'RollNo': record['student_roll'],
                    'FirstName': record['student_first'],
                    'LastName': record['student_last'],
                },
                'attended_lectures': record['attended_lectures'],
                'total_lectures': record['total_lectures'],
                'attendance_percentage': round(attendance_percentage, 2),
            })

        # Sort by roll number
        report_data.sort(key=lambda x: x['student']['RollNo'])

    context = {
        'teacher': teacher,
        'departments': departments,
        'selected_department': selected_department,
        'classes': classes,
        'selected_class': selected_class,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'report_data': report_data,
        'total_lectures': total_lectures,
        'subject_teacher': subject_teacher,
    }

    return render(request, 'subjectwise.html', context)
import json
from django.db.models import Q
@supabase_login_required
def leaves(request):
    try:
        email = request.session.get('teacher_email')
        teacher = get_object_or_404(Teacher.objects.select_related('RoleID', 'DepartmentID'), Email=email)
        role = teacher.RoleID.RoleName
        
        # Get teachers for approver dropdown
        teachers = []
        if role != 'HOD':
            teachers = Teacher.objects.filter(
                Q(DepartmentID=teacher.DepartmentID, RoleID__RoleName='HOD') |
                Q(RoleID__RoleName='Principal')
            )
        else:
            teachers = Teacher.objects.filter(RoleID__RoleName='Principal')

        if request.method == 'POST':
            try:
                data = request.POST
                leave_type_id = data.get('leaveType')
                start_date = data.get('startDate')
                end_date = data.get('endDate')
                requested_to_id = data.get('requestedTo')
                reason = data.get('reason')
                slots = data.getlist('slots[]')  # Get the slots data as a list

                # Validation code...

                # Create leave request
                leave_request = LeaveRequest.objects.create(
                    TeacherID=teacher,
                    LeaveTypeID_id=leave_type_id,
                    StartDate=start_date,
                    EndDate=end_date,
                    RequestedTo_id=requested_to_id,
                    Reason=reason,
                    Status='Pending'
                )

                # Handle time slots if provided
                print(slots)
                if slots:
                    for slot_data in slots:
                        try:
                            slot = json.loads(slot_data)
                            TempTimetable.objects.create(
                                LeaveRequestID=leave_request,
                                ClassID_id=slot['class'],
                                Date=slot['date'],
                                SlotID_id=slot['time_slot'],
                                ReplacementTeacherID_id=slot['replacement_teacher']
                            )
                        except json.JSONDecodeError as e:
                            logger.warning(f'Invalid slot data format: {e}')
                        except KeyError as e:
                            logger.warning(f'Missing slot data field: {e}')
                        except Exception as e:
                            logger.error(f'Error creating temp timetable entry: {e}')

                return JsonResponse({
                    'status': 'success',
                    'message': 'Leave request submitted successfully'
                })

            except Exception as e:
                logger.error(f'Error submitting leave request: {str(e)}')
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error submitting leave request: {str(e)}'
                }, status=500)

        # Get pending leaves for admin users with specific filtering
        pending_leaves = None
        if role == 'HOD':
            pending_leaves = LeaveRequest.objects.filter(
                Status='Pending',
                TeacherID__DepartmentID=teacher.DepartmentID,
                is_approvedByHOD=False
            ).prefetch_related(
                'temptimetable_set',
                'temptimetable_set__ClassID',
                'temptimetable_set__SlotID',
                'temptimetable_set__ReplacementTeacherID'
            ).select_related('TeacherID', 'LeaveTypeID')
        elif role == 'Principal':
            pending_leaves = LeaveRequest.objects.filter(
                Status='Pending Principal Approval',
                is_approvedByHOD=True,
                is_approvedByPrincipal=False
            ).prefetch_related(
                'temptimetable_set',
                'temptimetable_set__ClassID',
                'temptimetable_set__SlotID',
                'temptimetable_set__ReplacementTeacherID'
            ).select_related('TeacherID', 'LeaveTypeID')
        else:
            pending_leaves = LeaveRequest.objects.filter(
                TeacherID=teacher,
                Status__in=['Pending', 'Pending Principal Approval']
            ).prefetch_related(
                'temptimetable_set',
                'temptimetable_set__ClassID',
                'temptimetable_set__SlotID',
                'temptimetable_set__ReplacementTeacherID'
            ).select_related('TeacherID', 'LeaveTypeID')

        # No need to manually attach temp_slots as we're using prefetch_related
        
        # Get leave history with temp slots
        leave_history = LeaveRequest.objects.filter(
            TeacherID=teacher
        ).prefetch_related(
            'temptimetable_set',
            'temptimetable_set__ClassID',
            'temptimetable_set__SlotID',
            'temptimetable_set__ReplacementTeacherID'
        ).order_by('-RequestDate')

        # Get leave history and stats
        leave_history = LeaveRequest.objects.filter(TeacherID=teacher).order_by('-RequestDate')
        stats = {
            'approved': leave_history.filter(Status='Approved').count(),
            'pending': leave_history.filter(
                Q(Status='Pending') | 
                Q(Status='Pending Principal Approval')
            ).count(),
            'rejected': leave_history.filter(Status='Rejected').count()
        }

        # Get all active slots
        slots = Slots.objects.all().order_by('start_time')
        
        # Get all teachers except current teacher for replacement options
        all_teachers = TeacherSubjectAssignment.objects.filter(TeacherID__DepartmentID=teacher.DepartmentID).exclude(TeacherID=teacher.Teacherid).order_by('AssignmentID')
        classes=Classes.objects.filter(DepartmentID=teacher.DepartmentID)
        # Get teacher assignments for class selection
        teacher_assignments = TeacherSubjectAssignment.objects.filter(
            TeacherID=teacher
        ).select_related(
            'SubjectID__CurrentClassID'
        ).order_by('SubjectID__CurrentClassID__ClassName')

        context = {
            'teacher': teacher,
            'is_admin': role in ['HOD', 'Principal'],
            'leave_types': LeaveType.objects.all(),
            'teachers': teachers,
            'pending_leaves': pending_leaves,
            'leave_history': leave_history,
            'stats': stats,
            'slots': slots,
            'all_teachers': all_teachers,
            'teacher_assignments': teacher_assignments,
            'classes':classes,
        }

        return render(request, 'leaves.html', context)

    except Exception as e:
        logger.error(f'Error in leaves view: {str(e)}')
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your request'
        }, status=500)

@supabase_login_required
def leave_action(request, leave_id):
    """Handle leave approval/rejection"""
    if request.method == 'POST':
        try:
            email = request.session.get('teacher_email')
            teacher = get_object_or_404(Teacher.objects.select_related('RoleID'), Email=email)
            leave_request = get_object_or_404(LeaveRequest, LeaveRequestID=leave_id)
            
            action = request.POST.get('action', 'no_action')
            
            if action == 'no_action':
                return JsonResponse({
                    'status': 'error',
                    'message': 'No action specified'
                }, status=400)

            current_time = timezone.now()

            # Process based on role and action
            if teacher.RoleID.RoleName == 'HOD':
                if action == 'approve' and not leave_request.is_approvedByHOD:
                    leave_request.is_approvedByHOD = True
                    leave_request.HODApprovalDate = current_time
                    leave_request.Status = 'Pending Principal Approval'
                    leave_request.save()
                elif action == 'reject' and not leave_request.is_approvedByHOD:
                    leave_request.Status = 'Rejected'
                    leave_request.save()

            elif teacher.RoleID.RoleName == 'Principal':
                if action == 'approve' and leave_request.is_approvedByHOD and not leave_request.is_approvedByPrincipal:
                    leave_request.is_approvedByPrincipal = True
                    leave_request.PrincipalApprovalDate = current_time
                    leave_request.Status = 'Approved'
                    leave_request.save()
                elif action == 'reject' and not leave_request.is_approvedByPrincipal:
                    leave_request.Status = 'Rejected'
                    leave_request.save()

            # Return success response
            return redirect('/leaves')
            
        except Exception as e:
            logger.error(f'Error in leave_action: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    # If not POST, redirect to leaves page
    return redirect('/leaves')

def handler404(request, exception):
    context = {
        'error_title': '404 Not Found',
        'error_message': 'The page you are looking for does not exist.',
        'return_url': '/',
        'return_text': 'Return to Home'
    }
    return render(request, 'error.html', context, status=404)