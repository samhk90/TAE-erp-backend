from django.shortcuts import render,redirect,get_object_or_404
from .models import Notices,Timetable,Teacher,Subject,Student,Attendance,TeacherSubjectAssignment,Department,Year,Classes,ClassTeacherAssignment
from supabase import create_client, Client
url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
supabase: Client = create_client(url, key)
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
        teacher=True
        department=Teacher.objects.get(Email=email)
        department=department.DepartmentID
        today=date.today()
        timefrom="09:15 am"
        timeto='10:15 am'
        attendance_records = Attendance.objects.filter(ClassID__DepartmentID=department,Date=today,Timefrom=timefrom,Timeto=timeto).distinct()
        present_count = attendance_records.filter(ClassID__DepartmentID=department,Status=True).count()
        absent_count = attendance_records.filter(ClassID__DepartmentID=department,Status=False).count()
        total_count = Student.objects.filter(CurrentClassID__DepartmentID=department).count()
        print(total_count)
        if total_count > 0:
            attendance_percentage = (present_count / total_count) * 100
        else:
            attendance_percentage = 0 

        context = {
        'teacher':teacher,
        'present': present_count,
        'absent': absent_count,
        'total':total_count,
        'attendance_percentage': attendance_percentage,
    }
        return render(request,'index.html',context)
    elif  role.RoleName=='Principal':
        Principal=True
        today=date.today()
        timefrom="09:15 am"
        timeto='10:15 am'
        attendance_records = Attendance.objects.filter(Timefrom=timefrom,Timeto=timeto,Date=today).distinct()
        print(attendance_records)
        present_count = attendance_records.filter(Status=True).count()
        absent_count = attendance_records.filter(Status=False).count()
        total_count = Student.objects.all().count()
        if total_count > 0:
            attendance_percentage = (present_count / total_count) * 100
        else:
            attendance_percentage = 0 
        context = {
        'Principal':Principal,
        'present': present_count,
        'absent': absent_count,
        'total':total_count,
        'attendance_percentage': attendance_percentage,
    }
        return render(request,'index.html',context)
    return render(request, 'index.html',{'role':role})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('username1')
        password = request.POST.get('password')
        
        try:
            # Attempt to sign in with the provided credentials
            sign_in_data = supabase.auth.sign_in_with_password({'email': email, "password": password})
            user = sign_in_data.user
        except Exception as e:
            # Handle authentication error
            error_message = "Invalid login credentials. Please try again."
            return render(request, 'login.html', {'error_message': error_message})

        if user:
            request.session['teacher_email'] = email
            return redirect('index')  # Redirect to the index page after login

    return render(request, 'login.html')

def logout(request):
    request.session.flush()
    res = supabase.auth.sign_out()
    return redirect('login')

#student reg.
@supabase_login_required
def student(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        mothersname=request.POST.get('mothersname')
        fathersname=request.POST.get('fathersname')
        email = request.POST.get('email')
        password = '123456'  # Default password for demonstration; consider generating a secure password
        date_of_birth = request.POST.get('date_of_birth')
        Adharcardnumber = request.POST.get('Adharcardnumber')
        mobile_number = request.POST.get('mobile_number')
        father_number = request.POST.get('father_number')
        mother_number = request.POST.get('mother_number')
        gender = request.POST.get('gender')
        admission_type = request.POST.get('admission_type')
        category=request.POST.get('category')
        bloodgrp=request.POST.get('bloodgrp')
        course=request.POST.get('course')
        tempaddress = request.POST.get('tempaddress')
        permanetaddress = request.POST.get('permanetaddress')
        state = request.POST.get('state')
        city = request.POST.get('city')
        admission_date = request.POST.get('admission_date')
        print(email)
        
        try:
            # Sign up user with Supabase
            sign_up_response = supabase.auth.sign_up({
                'email': email,
                'password': password,
            })
            
            # Debugging information
            print("Sign up response:", sign_up_response)

            # Check if the sign up was successful
            if sign_up_response.user:
                user_id = sign_up_response.user.id  # Correct way to access the user ID
                # Print the user ID to verify
                print("User ID:", user_id)
                
                # Create a Student instance in the database
                student = Student.objects.create(
                    StudentID=user_id,
                    FirstName=firstname,
                    Email=email,
                    LastName=lastname,
                    PRN='123456',
                    RollNumber=00,
                    FatherName=fathersname,
                    FatherContact=father_number,
                    MotherName=mothersname,
                    MotherContact=mother_number,
                    MobileNumber=mobile_number,
                    AdharNumber=Adharcardnumber,
                    DOB=date_of_birth,
                    Gender=gender,
                    AdmissionQuota=admission_type,
                   Category=category,
                   Bloodgrp=bloodgrp,
                   permenentadd=permanetaddress,
                   tempadd=tempaddress,
                   YearDownStatus='False',
                   
                )

                messages.success(request, 'Student registered successfully.')
                return redirect('student')  # Redirect to a success page

        except Exception as e:
            error_message = str(e)
            print("Exception:", error_message)  # Print exception for debugging
            messages.error(request, error_message)
            return render(request, 'student_form.html')

    return render(request, 'student_form.html')

@supabase_login_required
def academics(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    role = teacher.RoleID.RoleName
    role1 = ClassTeacherAssignment.objects.filter(TeacherID=teacher.Teacherid).first()

    # Determine roles
    is_teacher = role == 'Teacher'
    is_classteacher = role1 and role1.RoleID.RoleName == 'Classteacher'
    principal=role=='Principal'
    if request.method == 'POST':
        class_id = request.POST.get('id')
        selected_class = request.POST.get('class')
        subject_id = request.POST.get('sub')
        batch=request.POST.get('batch')
        if class_id and selected_class and subject_id :
            # Redirect to attendance_form view
            return redirect('attendance_form', sub=subject_id, id=class_id, class_name=selected_class,batch=batch)
        elif class_id and selected_class and subject_id and batch:
            # Redirect to attendance_form view
            return redirect('attendance_form', sub=subject_id, id=class_id, class_name=selected_class,batch=batch)
        else:
            messages.error(request, "Invalid form submission.")
            return redirect('academics')

    assignments = TeacherSubjectAssignment.objects.filter(TeacherID=teacher.Teacherid)
    subjects = [assignment.SubjectID for assignment in assignments]
    subject_deps = Subject.objects.filter(SubjectName__in=subjects).values_list('Subjectdep', flat=True)
    subject_yrs = Subject.objects.filter(SubjectName__in=subjects).values_list('Subjectyr', flat=True)

# Filter classes that match the department and year of the subjects
    assigned_classes = Classes.objects.filter(
    DepartmentID__in=subject_deps,
    YearID__in=subject_yrs
).distinct()
    context = {
        'principal':principal,
        'is_classteacher': is_classteacher,
        'is_teacher': is_teacher,
        'subjects': subjects,
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
def attendance_form(request, sub, id, class_name,batch):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)

    if request.method == 'POST':
        # Handle attendance submission
        date = request.POST.get('date')
        time_to = request.POST.get('to_time')
        time_from = request.POST.get('from_time')

        subject = get_object_or_404(Subject, SubjectID=sub)
        if subject.SubjectType==False:
            batch=int(batch)
            students=Student.objects.filter(CurrentClassID=class_name,batch=batch).order_by('RollNumber')
        else:
            students = Student.objects.filter(CurrentClassID=class_name).order_by('RollNumber')

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
    subject = get_object_or_404(Subject, SubjectID=sub)
    if subject.SubjectType==False:
            batch=int(batch)
            students=Student.objects.filter(CurrentClassID=class_name,batch=batch).order_by('RollNumber')
    else:
            students = Student.objects.filter(CurrentClassID=class_name).order_by('RollNumber')

    class_name=Classes.objects.get(ClassID=class_name)
    subjecttype=subject.SubjectType
    context = {
        'subjecttype':subjecttype,
        'students': students,
        'teacher': teacher,
        'subject': subject,
        'selected_class': class_name,
        'batch':batch
    }
    return render(request, 'attendance_form.html', context)
@supabase_login_required
@supabase_login_required
def students(request):
    year = Year.objects.all()
    department = Department.objects.all()

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
        }

        return render(request, 'students.html', context)

    return render(request, 'students.html', {'year': year, 'department': department})

@supabase_login_required
def notices(request):
    allnotices= Notices.objects.order_by('-date')
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    return render(request, 'notices.html',{'notice': allnotices,'teacher':teacher})
@supabase_login_required
def edit_notice(request):
    noticeid = request.GET.get('noticeid')
    teacher_id = request.GET.get('id')
    notice = Notices.objects.get(id=noticeid)
    teacher=Teacher.objects.get(Teacherid=teacher_id)
    if request.method == 'POST':
        title = request.POST.get('noticeTitle')
        description = request.POST.get('noticeBody')
        date = request.POST.get('noticeDate')
        attachment = request.FILES.get('noticeattachment')
        year=request.POST.get('year')
        department=request.POST.get('department')
        notice.title = title
        notice.description = description
        notice.date = date
        notice.attachment = attachment
        notice.year=year
        notice.derpartment=department


        notice.save()
        notice=Notices.objects.order_by('-date')
        return render(request, 'notice.html', {'notice': notice,'teacher':teacher})

    return render(request, 'noticeform.html', {'notice': notice})
@supabase_login_required
def noticeform(request):
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id)
    if request.method == 'POST':
        title = request.POST.get('noticeTitle')
        description = request.POST.get('noticeBody')
        date = request.POST.get('noticeDate')
        year=request.POST.get('year')
        department=request.POST.get('department')
        attachment = request.FILES.get('noticeattachment')
        notice = Notices.objects.create(
            title=title,
            description=description,
            date=date,
            attachment=attachment.name,
            year=year,
            derpartment=department
        )
        allnotices=Notices.objects.order_by('-date')
        return render(request,'notice.html',{'notice': allnotices,'teacher':teacher})  
    else:
        return render(request, 'noticeform.html',{'teacher':teacher})
@supabase_login_required
def delete_notice(request): 
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id) 
    notice_id = request.POST.get('notice_id') 
    Notices.objects.filter(id=notice_id).delete() 
    allnotice=Notices.objects.order_by('-date')
    return render(request,'notice.html',{'teacher':teacher,'notice':allnotice}) 

from django.shortcuts import render
from django.db.models import Count
from .models import Attendance
from django.utils import timezone
def logs(request):
    # Get today's date
    today = timezone.now().date()
    
    # Query attendance records for today and join with TeacherSubjectAssignment to get faculty names
    attendance_records = Attendance.objects.select_related('SubjectID').filter(Date=today).values(
        'Timefrom', 'Timeto', 'SubjectID__SubjectName','SubjectID__SubjectDepartment','SubjectID__SubjectYear','SubjectID__teachersubjectassignment__TeacherID__FirstName'
    ).annotate(
        student_count=Count('StudentID')
    ).order_by('Timefrom', 'Timeto')
    
    # Context to pass data to the template
    context = {
        'attendance_records': attendance_records,
    }
    return render(request,'logs.html',context)