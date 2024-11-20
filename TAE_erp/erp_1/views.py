from django.shortcuts import render,redirect,get_object_or_404
from .models import Notices,Timetable,Teacher,Subject,Student,Attendance,TeacherSubjectAssignment,Department,Year,Classes,ClassTeacherAssignment
from supabase import create_client, Client,SupabaseAuthClient
from django.core.serializers import serialize
from django.shortcuts import render
from erp_1.decorators import supabase_login_required  # Adjust the import path accordingly
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Teacher, ClassTeacherAssignment, Student, Attendance,Slots
from datetime import date

from datetime import timedelta
from django.utils import timezone
from collections import defaultdict
from django.db.models import Case, When, IntegerField
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Notices
import supabase
@supabase_login_required
def index(request):
    email = request.session.get('teacher_email')
    today = date.today()
    timefrom = "09:15 am"
    timeto = "10:15 am"
    try:
        teacher = Teacher.objects.select_related('RoleID', 'DepartmentID').get(Email=email)
        role = teacher.RoleID.RoleName
    except Teacher.DoesNotExist:
        return render(request, 'index.html', {'error_message': 'Teacher not found'})
    if role == 'Teacher':
        department = teacher.DepartmentID
        attendance_records = Attendance.objects.filter(
            ClassID__DepartmentID=department, Date=today, Timefrom=timefrom, Timeto=timeto
        ).distinct()
        if not attendance_records.exists():
            timeto = '11:15 am'
            attendance_records = Attendance.objects.filter(
                ClassID__DepartmentID=department, Date=today, Timefrom=timefrom, Timeto=timeto
            ).distinct()
        attendance_summary = attendance_records.values('ClassID__DepartmentID').annotate(
            present_count=Count('Status', filter=Q(Status=True)),
            absent_count=Count('Status', filter=Q(Status=False))
        ).order_by('AttendanceID').first()

        present_count = attendance_summary['present_count'] if attendance_summary else 0
        absent_count = attendance_summary['absent_count'] if attendance_summary else 0
        total_count = Student.objects.filter(CurrentClassID__DepartmentID=department).count()

        attendance_percentage = (present_count / total_count) * 100 if total_count > 0 else 0

        context = {
            'teacher': teacher,
            'present': present_count,
            'absent': absent_count,
            'total': total_count,
            'attendance_percentage': attendance_percentage,
        }
        return render(request, 'index.html', context)

    elif role == 'Principal':
        attendance_records = Attendance.objects.filter(
             Date=today, Timefrom=timefrom, Timeto=timeto
        ).distinct()
        if not attendance_records.exists():
            timeto = '11:15 am'
            attendance_records = Attendance.objects.filter(
                 Date=today, Timefrom=timefrom, Timeto=timeto
            ).distinct()
        attendance_summary = attendance_records.values('ClassID__DepartmentID').annotate(
            present_count=Count('Status', filter=Q(Status=True)),
            absent_count=Count('Status', filter=Q(Status=False))
        ).order_by('AttendanceID').first()

        present_count = attendance_summary['present_count'] if attendance_summary else 0
        absent_count = attendance_summary['absent_count'] if attendance_summary else 0
        total_count = Student.objects.all().count()

        attendance_percentage = (present_count / total_count) * 100 if total_count > 0 else 0

        context = {
            'teacher': teacher,
            'present': present_count,
            'absent': absent_count,
            'total': total_count,
            'attendance_percentage': attendance_percentage,
        }
        return render(request, 'index.html', context)

    return render(request, 'index.html', {'teacher': teacher})


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
                return redirect('index')
                 # Redirect to the index page after login

        except Exception as e:
            # Handle authentication error
            error_message = "Invalid login credentials. Please try again."
            print(e)  # Print the error for debugging
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def logout(request):
    url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
    key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9zZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
    supabase: Client = create_client(url, key)

    try:
        res = supabase.auth.sign_out()
    except Exception as e:
        print(e)
    
    request.session.flush()
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
        assignments = TeacherSubjectAssignment.objects.filter(TeacherID=teacher.Teacherid)
        subject_ids = [assignment.SubjectID.SubjectID for assignment in assignments]
        if batch == 'All':
            subjects = Subject.objects.filter(SubjectID__in=subject_ids, CurrentClassID=selected_class, SubjectType=True)
        else:
            subjects = Subject.objects.filter(SubjectID__in=subject_ids, CurrentClassID=selected_class, SubjectType=False)

        class_ids = Subject.objects.filter(SubjectID__in=subject_ids).values_list('CurrentClassID', flat=True).distinct()
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
            return redirect('academics')  # Redirect back to the same form with the error message

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
                Status=is_present,
                ClassID=Classes.objects.get(ClassID=selected_class)
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
def report(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    assignments = TeacherSubjectAssignment.objects.filter(TeacherID=teacher.Teacherid)
    subject_ids = [assignment.SubjectID.SubjectID for assignment in assignments]

        # Filter subjects based on the selected class and the subject IDs from the assignments
    subjects = Subject.objects.filter(SubjectID__in=subject_ids)
    class_ids = Subject.objects.filter(SubjectID__in=subject_ids).values_list('CurrentClassID', flat=True).distinct()
        
        # Fetch the classes using the class IDs
    assigned_classes = Classes.objects.filter(ClassID__in=class_ids)
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        selected_subject = request.POST.get('subject')
        selected_class = request.POST.get('class')
        selected_class=Classes.objects.get(ClassID=selected_class)
    # Get students in the assigned class
        students = Student.objects.filter(CurrentClassID=selected_class).order_by('RollNumber')
        
    # Initialize attendance data list
        attendance_data = []
        subjects_set = set()
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_date = None
            end_date = None

        attendance_data = []
        subjects_set = set()
        for student in students:
            student_attendance = Attendance.objects.filter(
        StudentID=student.StudentID,
        SubjectID=selected_subject,
        Date__range=(start_date, end_date)  # Filter by date range
    ).values('SubjectID', 'SubjectName').annotate(
        attended_count=Count('AttendanceID', filter=Q(Status=True)),
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
        'attendance_data': attendance_data,
        'subjects': subjects,
        'classes': assigned_classes,
        'start_date': start_date,
        'end_date': end_date,
        'selected_subject': selected_subject,
        'selected_class': selected_class,
    }
        return render(request, 'attendance_report.html', context)
    # Render the template with the context data
    context = {
        'teacher': teacher,
        'subjects': subjects,
        'classes': assigned_classes,
    }
    return render(request, 'attendance_report.html', context)

@supabase_login_required
def preacademic(request):
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    classteacher = False

    try:
        assignment = ClassTeacherAssignment.objects.get(TeacherID=teacher.Teacherid)
        role = assignment.RoleID
        if role.RoleName == 'Classteacher':
            classteacher = True
    except ClassTeacherAssignment.DoesNotExist:
        # Handle case when no assignment is found, defaulting to classteacher=False
        classteacher = False
    context={
        'teacher': teacher,
        'classteacher':classteacher
    }
    return render(request,'preacademic.html',context)
@supabase_login_required
def timetable(request): 
    email = request.session.get('teacher_email')
    teacher = Teacher.objects.get(Email=email)
    classes=Classes.objects.filter(DepartmentID=teacher.DepartmentID)
    selected_timetable_type = request.GET.get('timetable_type')  # Default to 'Master'
    timetable_entries = None
    day_order = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }
    
    # Annotate the timetable entries with a numerical value for sorting
    timetable_entries = Timetable.objects.filter(ClassID__ClassID=selected_timetable_type).annotate(
        day_order=Case(
            *[When(Day=day, then=value) for day, value in day_order.items()],
            output_field=IntegerField(),
        )
    ).order_by('day_order', 'SlotID')
    
    # Preprocess timetable entries for unique day and slot ID
    timetable = defaultdict(lambda: defaultdict(list))  # Nested defaultdict for day -> slot ID -> entries
    slot_list = set()  # Store unique slots for display in template
    
    for entry in timetable_entries:
        # Group by day and slot
        timetable[entry.Day][entry.SlotID].append(entry.SubjectAssignmentID)
        slot_list.add(entry.SlotID)  # Keep track of unique slots
    
    # Convert timetable structure for easy access in the template
    processed_timetable = {
        day: {
            slot: assignments for slot, assignments in slots.items()
        } for day, slots in timetable.items()
    }
    print(processed_timetable.items())
    
    context = {
        'timetable': processed_timetable.items(),
        'classes': classes,
        'selected_timetable_type': selected_timetable_type,
        'slot_list': slot_list,
        'teacher': teacher
    }
    
    return render(request, 'timetable.html', context)

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

@supabase_login_required
def history(request):
    return render(request,'history.html')

@supabase_login_required
def preports(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    context={
        'teacher':teacher
    }
    return render(request,'preports.html',context)

@supabase_login_required
def custom_report(request):
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
        print(selected_department)
    else:
        selected_department = request.GET.get('department')
    
    selected_class = request.GET.get('class')
    if selected_department:
        classes = Classes.objects.filter(DepartmentID=selected_department)
    else:
        classes = Classes.objects.all()

    current_date = timezone.now().date()
    current_date=current_date-timedelta(1)


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
        if isinstance(class_obj, Classes):
            attendance_records = Attendance.objects.filter(Date__range=(start_date, end_date), ClassID=class_obj)
        else:
            attendance_records = Attendance.objects.filter(Date__range=(start_date, end_date), ClassID__in=class_obj)

        # Collect attendance data for each student in the class
        students_in_class = Student.objects.filter(CurrentClassID__in=class_obj)

        # Pre-fetch attendance counts per day for each student to minimize DB hits
        attendance_counts = (
            attendance_records
            .values('StudentID', 'Date')
            .annotate(attended_count=Count('SlotID', filter=Q(Status=True)), conducted_count=Count('SlotID'))
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

from django.db.models import Count, F, Q
@supabase_login_required
def subjectwise_report(request):
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
    if selected_class:
        selected_subject = request.GET.get('subject')
        subjects = Subject.objects.filter(CurrentClassID=selected_class)
    else:
        selected_subject=None
        subjects=None
    report_data = []
    total_lectures = 0
    teachert=None
    if selected_class and selected_subject:
        teachert=TeacherSubjectAssignment.objects.filter(SubjectID=selected_subject)
        total_lectures = Attendance.objects.filter(
            ClassID=selected_class,
            SubjectID=selected_subject
        ).values('Date').distinct().count()
        attendance_data = (
            Attendance.objects.filter(
                ClassID=selected_class,
                SubjectID=selected_subject
            )
            .values('StudentID')
            .annotate(
                attended_lectures=Count('AttendanceID', filter=Q(Status=True)),
                student_roll=F('StudentID__RollNumber'),
                student_first=F('StudentID__FirstName'),
                student_last=F('StudentID__LastName'),
            ).order_by('student_roll')
        )
        for record in attendance_data:
            attendance_percentage = (
                (record['attended_lectures'] / total_lectures * 100)
                if total_lectures > 0
                else 0
            )
            report_data.append({
                'student': {
                    'RollNo': record['student_roll'],
                    'FirstName': record['student_first'],
                    'LastName': record['student_last'],
                },
                'attended_lectures': record['attended_lectures'],
                'attendance_percentage': attendance_percentage,
            })
            

    context = {
        'teacher': teacher,
        'departments':departments,
        'selected_department':selected_department,
        'classes': classes,
        'selected_class': selected_class,
        'subjects': subjects,
        'selected_subject': selected_subject,
        'report_data': report_data,
        'total_lectures': total_lectures,
        'teachert':teachert,
    }

    return render(request, 'subjectwise.html', context)

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