from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from .models import Notices,Timetable,Teacher,Subject,Student,Attendance,Teacher_Subject_Assignment
from supabase import create_client, Client
from django.db.models import Count
url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
supabase: Client = create_client(url, key)
from django.core.serializers import serialize


def index(request):
    if request.method=='POST':
        email=request.POST.get('username1')
        password=request.POST.get('password')
        sign_in_data = supabase.auth.sign_in_with_password({'email':email, "password":password})        
        user = sign_in_data.user
        print(user)
        teacher=Teacher.objects.get(Email=email)
        if teacher:
            request.session['teacher_email'] = teacher.Email
            return render(request, 'index.html', {'teacher':teacher})
        return render(request, 'index.html', {'teacher':teacher})

    return render(request, 'login.html')
def main(request):

     return render(request, 'index.html')
def signout(request):
    res = supabase.auth.sign_out()
    return redirect('index')

from django.shortcuts import render, redirect
from django.contrib import messages

def student(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = '123456'  # Default password for demonstration; consider generating a secure password
        date_of_birth = request.POST.get('date_of_birth')
        course = request.POST.get('course')
        mobile_number = request.POST.get('mobile_number')
        gender = request.POST.get('gender')
        admission_type = request.POST.get('admission_type')
        address = request.POST.get('address')
        state = request.POST.get('state')
        city = request.POST.get('city')
        admission_date = request.POST.get('admission_date')
        passing_year = request.POST.get('passing_year')
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
                    First_name=full_name,
                    Email_id=email,
                    Last_name='samee',
                    PRN='123456',
                    Year='2021',
                    Department='Computer',
                    division='A',
                    Category='General',
                    Roll_number='1',
                )

                messages.success(request, 'Student registered successfully.')
                return redirect('main')  # Redirect to a success page

        except Exception as e:
            error_message = str(e)
            print("Exception:", error_message)  # Print exception for debugging
            messages.error(request, error_message)
            return render(request, 'student.html')

    return render(request, 'student.html')


def academics(request):
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    id=teacher.Teacherid
    assignments = Teacher_Subject_Assignment.objects.filter(TeacherID=id)
    subjects = [assignment.SubjectID for assignment in assignments]
    return render(request, 'academics.html',{'subjects':subjects})
def greenbook(request):
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    department=teacher.Department
    print(teacher.Department)
    students=Student.objects.filter(Year='BE',Department=department)
    print(students)
    return render(request,'green.html',{'students':students})

from django.contrib import messages

def attendance_form(request):
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    id=teacher.Teacherid
    if request.method == 'POST':
        date = request.POST.get('date')
        time_to = request.POST.get('to_time')
        time_from = request.POST.get('from_time')
        classid = request.GET.get('id')
        subject_id=request.GET.get('sub')
        print(subject_id)
        teacher=Teacher.objects.get(Teacherid=id)
        assignments = Teacher_Subject_Assignment.objects.filter(TeacherID=id)
        subjects = [assignment.SubjectID for assignment in assignments]
        subject=Subject.objects.get(SubjectID=subject_id)
        subjectname=subject.SubjectName
        subjectType=subject.SubjectType
        if subjectType=='Theoretical':
            students=Student.objects.filter(CurrentClassID=classid).order_by('RollNumber')
        else:
            students=Student.objects.filter(CurrentClassID=classid).order_by('RollNumber')
        jsonlist=[]
        for student in students:
            is_present = request.POST.get(f'is_present_{student.StudentID}') == 'on'
        

            jsonlist.append({
            'StudentID':student,
            'Date': date,
            'Timeto': time_to,
            'Timefrom': time_from,
            'SubjectID': subject,
            'ClassID_id':classid,
            'SubjectName': subjectname,
            'Status': is_present
            })

        Attendance.objects.bulk_create([
            Attendance(**data) for data in jsonlist
        ])
        messages.success(request, 'Attendance has been marked successfully')
        return render(request, 'academics.html',{'subjects':subjects,'teacher':teacher})    

    else:
        email=request.session.get('teacher_email')
        teacher=Teacher.objects.get(Email=email)
        id=teacher.Teacherid
        subject_id = request.GET.get('sub')
        classid = request.GET.get('id')
        subject = Subject.objects.get(SubjectID=subject_id)
        subjectType=subject.SubjectType
        if subjectType==True:
            students=Student.objects.filter(CurrentClassID=classid).order_by('RollNumber')
        else:
            students=Student.objects.filter(CurrentClassID=classid).order_by('RollNumber')
        return render(request, 'attendance_form.html', {'students': students, 'teacher': teacher, 'subject': subject})

def info_2(request):
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id)
    students = Student.objects.all()
    teaher=Teacher.objects.all()
    return render(request, 'info_2.html', {'students': students,'teacher':teacher,'teaher':teaher})

def student_info(request):
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id)
    prn = request.GET.get('prn')
    student_info = Student.objects.get(PRN=prn)
    return render(request, 'student_info.html', {'student_info': student_info,'teacher':teacher})
def notices(request):
    allnotices= Notices.objects.order_by('-date')
    email=request.session.get('teacher_email')
    teacher=Teacher.objects.get(Email=email)
    return render(request, 'notice.html',{'notice': allnotices,'teacher':teacher})

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
def delete_notice(request): 
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id) 
    notice_id = request.POST.get('notice_id') 
    Notices.objects.filter(id=notice_id).delete() 
    allnotice=Notices.objects.order_by('-date')
    return render(request,'notice.html',{'teacher':teacher,'notice':allnotice}) 