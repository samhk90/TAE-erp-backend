from django.shortcuts import render,redirect,get_object_or_404
from .models import Notices,Timetable,Teacher,Subject,Student,Attendance,TeacherSubjectAssignment,Department,Year,Classes,ClassTeacherAssignment
from supabase import create_client, Client,SupabaseAuthClient
url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
supabase: Client = create_client(url, key)
from supabase_auth import AuthResponse
from django.core.serializers import serialize
from django.shortcuts import render
from erp_1.decorators import supabase_login_required  # Adjust the import path accordingly
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Teacher, ClassTeacherAssignment, Student, Attendance
from datetime import date
@supabase_login_required
def index(request):
    email=request.session.get('teacher_email')
    role=Teacher.objects.get(Email=email).RoleID
    if role.RoleName=='Teacher':
        department=Teacher.objects.get(Email=email)
        department=department.DepartmentID
        today=date.today()
        timefrom="09:15 am"
        timeto='10:15 am'
        attendance_records = Attendance.objects.filter(ClassID__DepartmentID=department,Date=today,Timefrom=timefrom,Timeto=timeto).distinct()
        present_count = attendance_records.filter(ClassID__DepartmentID=department,Status=True).count()
        absent_count = attendance_records.filter(ClassID__DepartmentID=department,Status=False).count()
        total_count = Student.objects.filter(CurrentClassID__DepartmentID=department).count()
        if total_count > 0:
            attendance_percentage = (present_count / total_count) * 100
        else:
            attendance_percentage = 0 
        email=request.session.get('teacher_email')
        teacher=Teacher.objects.get(Email=email)
        context = {
        'teacher':teacher,
        'present': present_count,
        'absent': absent_count,
        'total':total_count,
        'attendance_percentage': attendance_percentage,
    }
        return render(request,'index.html',context)
    elif  role.RoleName=='Principal':
        today=date.today()
        timefrom="09:15 am"
        timeto='10:15 am'
        attendance_records = Attendance.objects.filter(Timefrom=timefrom,Timeto=timeto,Date=today).distinct()
        present_count = attendance_records.filter(Status=True).count()
        absent_count = attendance_records.filter(Status=False).count()
        total_count = Student.objects.all().count()
        if total_count > 0:
            attendance_percentage = (present_count / total_count) * 100
        else:
            attendance_percentage = 0 
        email=request.session.get('teacher_email')
        teacher=Teacher.objects.get(Email=email)
        context = {
        'teacher':teacher,
        'present': present_count,
        'absent': absent_count,
        'total':total_count,
        'attendance_percentage': attendance_percentage,
    }
        return render(request,'index.html',context)
    return render(request, 'index.html',{'role':role})
# Inspect the 'auth' attribute of the client



def login(request):
    if request.method == 'POST':
        email = request.POST.get('username1').replace(' ', '')
        password = request.POST.get('password')
        url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
        key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
        supabase: Client = create_client(url, key)
        try:
            response =supabase.auth.sign_in_with_password({'email':email,'password':password})
            user = response.user

            if user:
                request.session['teacher_email'] = email  
                return redirect('index')  # Redirect to the index page after login

        except Exception as e:
            # Handle authentication error
            error_message = "Invalid login credentials. Please try again."
            print(e)  # Print the error for debugging
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def logout(request):
    request.session.flush()
    url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
    supabase: Client = create_client(url, key)
    res = supabase.auth.sign_out()
    return redirect('login')

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
        # Check if the request is a CSV file upload
        if 'csv_file' in request.FILES:
            csv_file = request.FILES['csv_file']

            # Check if the uploaded file is a CSV file
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return render(request, 'student_form.html')

            try:
                # Read the CSV file
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
                key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
                supabase: Client = create_client(url, key)
                res = supabase.auth.sign_out()
                
                for row in reader:
                    # Extract student data from each row
                    firstname = row['firstname']
                    lastname = row['lastname']
                    email = row['email']
                    password = '123456'  
                    mobile_number = row['mobile_number']
                    RollNumber=row['rollnumber']
                    classid=row['classid']
                    try:
                        # Sign up user with Supabase
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
def academics(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    role1 = ClassTeacherAssignment.objects.filter(TeacherID=teacher.Teacherid).first()
    is_classteacher = role1 and role1.RoleID.RoleName == 'Classteacher'

    if request.method == 'POST':
        selected_class = request.POST.get('class')
        batch = request.POST.get('batch')

        # Get the subjects assigned to the teacher
        assignments = TeacherSubjectAssignment.objects.filter(TeacherID=teacher.Teacherid)
        subject_ids = [assignment.SubjectID.SubjectID for assignment in assignments]

        # Filter subjects based on the selected class and the subject IDs from the assignments
        subjects = Subject.objects.filter(SubjectID__in=subject_ids, CurrentClassID=selected_class)
        
        # Get the unique class IDs associated with the assigned subjects
        class_ids = Subject.objects.filter(SubjectID__in=subject_ids).values_list('CurrentClassID', flat=True).distinct()
        
        # Fetch the classes using the class IDs
        assigned_classes = Classes.objects.filter(ClassID__in=class_ids)
        
        context = {
            'is_classteacher': is_classteacher,
            'subjects': subjects,
            'selected_class': selected_class,
            'batch': batch,
            'teacher': teacher,
            'classes': assigned_classes,
        }
        return render(request, 'academics.html', context)
    assignments = TeacherSubjectAssignment.objects.filter(TeacherID=teacher.Teacherid)
    subject_ids = [assignment.SubjectID.SubjectID for assignment in assignments]

        # Filter subjects based on the selected class and the subject IDs from the assignments
    subjects = Subject.objects.filter(SubjectID__in=subject_ids)
    class_ids = Subject.objects.filter(SubjectID__in=subject_ids).values_list('CurrentClassID', flat=True).distinct()
        
        # Fetch the classes using the class IDs
    assigned_classes = Classes.objects.filter(ClassID__in=class_ids)

    context = {
        'is_classteacher': is_classteacher,
        'teacher': teacher,
        'classes': assigned_classes,
    }
    return render(request, 'academics.html', context)

@supabase_login_required
def greenbook(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    role=ClassTeacherAssignment.objects.get( TeacherID=teacher.Teacherid).RoleID
    if role.RoleName=='Classteacher':
            classteacher=True
    else:
            classteacher=False
    assignment = get_object_or_404(ClassTeacherAssignment, TeacherID=teacher.Teacherid)
    students = Student.objects.filter(CurrentClassID=assignment.ClassID).order_by('RollNumber')
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
        'classteacher':classteacher,
        'teacher': teacher,
        'attendance_data': attendance_data,
        'subjects': subjects_list,
    }
    return render(request, 'green.html', context)
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Attendance, Teacher, Subject, Student, ClassTeacherAssignment, Classes
from django.core.exceptions import ValidationError

@supabase_login_required
def attendance_form(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    selected_class = request.GET.get('class')
    subject_id = request.GET.get('sub')
    batch = request.GET.get('batch')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        time_to = request.POST.get('to_time')
        time_from = request.POST.get('from_time')
        subject = get_object_or_404(Subject, SubjectID=subject_id)

        # Check for existing attendance records
        existing_attendance = Attendance.objects.filter(
            Date=date,
            Timefrom=time_from,
            Timeto=time_to,
            SubjectID=subject
        ).exists()

        if existing_attendance:
            # If attendance already exists, show an error message
            messages.error(request, 'Attendance already exists for the selected date and time. Please change the date or time.')
            return redirect(request.path_info)  # Redirect back to the same form with the error message

        if subject.SubjectType == False:
            batch = int(batch)  # Ensure batch is an integer if needed
            students = Student.objects.filter(CurrentClassID=selected_class, batch=batch).order_by('RollNumber')
        else:
            students = Student.objects.filter(CurrentClassID=selected_class).order_by('RollNumber')

        attendance_records = []
        for student in students:
            is_present = request.POST.get(f'is_present_{student.StudentID}') == 'on'
            attendance_records.append(Attendance(
                StudentID=student,
                Date=date,
                Timeto=time_to,
                Timefrom=time_from,
                SubjectID=subject,
                SubjectName=subject.SubjectName,
                Status=is_present
            ))

        Attendance.objects.bulk_create(attendance_records)
        messages.success(request, 'Attendance has been marked successfully.')
        return redirect('academics')

    # If GET request or form not submitted
    subject = get_object_or_404(Subject, SubjectID=subject_id)
    
    if subject.SubjectType == False:
        batch = int(batch)  # Ensure batch is an integer if needed
        students = Student.objects.filter(CurrentClassID=selected_class, batch=batch).order_by('RollNumber')
    else:
        students = Student.objects.filter(CurrentClassID=selected_class).order_by('RollNumber')

    subjecttype = subject.SubjectType
    role1 = ClassTeacherAssignment.objects.filter(TeacherID=teacher.Teacherid).first()
    is_classteacher = role1 and role1.RoleID.RoleName == 'Classteacher'
    selected_class = Classes.objects.get(ClassID=selected_class)
    
    context = {
        'subjecttype': subjecttype,
        'students': students,
        'teacher': teacher,
        'subject': subject,
        'selected_class': selected_class,
        'batch': batch,
        'is_classteacher': is_classteacher
    }
    return render(request, 'attendance_form.html', context)
@supabase_login_required
def students(request):
    year = Year.objects.all()
    department = Department.objects.all()
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    if request.method == 'POST':
        yearid = request.POST.get('year')
        departmentid = request.POST.get('department')
        currentclass = get_object_or_404(Classes, DepartmentID=departmentid, YearID=yearid)
        currentclassid = currentclass.ClassID
        students = Student.objects.filter(CurrentClassID=currentclassid).order_by('RollNumber')

        students_data = []
        subjects_set = set()

        for student in students:
            student_attendance = Attendance.objects.filter(StudentID=student.StudentID).values('SubjectID', 'SubjectName').annotate(
                attended_count=Count('AttendanceID', filter=Q(Status=True)),
                total_lectures=Count('Date')
            )

            total_attended = sum([subject['attended_count'] for subject in student_attendance])
            total_conducted = sum([subject['total_lectures'] for subject in student_attendance])
            average_percentage = (total_attended / total_conducted) * 100 if total_conducted > 0 else 0

            students_data.append({
                'student': student,
                'attendance': list(student_attendance),
                'total_attended': total_attended,
                'average_percentage': average_percentage,
            })

        context = {
            'year': year,
            'department': department,
            'students_data': students_data,
            'teacher':teacher
        }

        return render(request, 'students.html', context)

    return render(request, 'students.html', {'year': year, 'department': department,'teacher':teacher})

@supabase_login_required
def notices(request):
    allnotices= Notices.objects.order_by('-date')
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    role=teacher.RoleID.RoleName
    is_teacher = role == 'Teacher' 
    department=teacher.DepartmentID.DepartmentName
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


from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Notices
import supabase

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


from django.shortcuts import render
from django.db.models import Count
from .models import Attendance
from django.utils import timezone
@supabase_login_required
def logs(request):
    # Get the email of the logged-in teacher from the session
    email = request.session.get('teacher_email')
    teacher = Teacher.objects.get(Email=email)

    # Get today's date
    today = timezone.now().date()

    if teacher.RoleID.RoleName == 'Teacher':
        # Query attendance records only for the classes taken by the logged-in teacher
        attendance_records = Attendance.objects.select_related('SubjectID').filter(
            Date=today,
            SubjectID__teachersubjectassignment__TeacherID=teacher
        ).values(
            'Timefrom', 
            'Timeto', 
            'SubjectID__SubjectName',
            'SubjectID__SubjectDepartment',
            'SubjectID__SubjectYear',
            'SubjectID__teachersubjectassignment__TeacherID__FirstName'
        ).annotate(
            student_count=Count('StudentID')
        ).order_by('Timefrom', 'Timeto')

        context = {
            'attendance_records': attendance_records,
            'teacher': teacher
        }
        return render(request, 'tlogs.html', context)

    elif teacher.RoleID.RoleName == 'Principal':
        # Query attendance records for all classes since Principal can view all
        attendance_records = Attendance.objects.select_related('SubjectID').filter(
            Date=today
        ).values(
            'Timefrom', 
            'Timeto', 
            'SubjectID__SubjectName',
            'SubjectID__SubjectDepartment',
            'SubjectID__SubjectYear',
            'SubjectID__teachersubjectassignment__TeacherID__FirstName'
        ).annotate(
            student_count=Count('StudentID')
        ).order_by('Timefrom', 'Timeto')

        context = {
            'attendance_records': attendance_records,
            'teacher': teacher
        }
        return render(request, 'logs.html', context)

@supabase_login_required
def history(request):
    return render(request,'history.html')