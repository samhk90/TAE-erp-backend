from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from .models import Notices,Timetable,Teacher,Teacher_Subject_Assignment,Subject,Student,Attendance
# from supabase import create_client, Client
from django.db.models import Count
url: str = "https://gipdgkwmxmmykyaliwhr.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdpcGRna3dteG1teWt5YWxpd2hyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDU1OTg4NTIsImV4cCI6MjAyMTE3NDg1Mn0.GrCKjv0gzqFMRr5l3iTEWSa79LX2HU4P0KjEmWxfkKI"
# supabase: Client = create_client(url, key)


def index(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        # sign_in_data = supabase.auth.sign_in_with_password({'email':email, "password":password})
        # user = sign_in_data.user
        teacher=Teacher.objects.get(Email=email)
        if teacher:
            timetable=Timetable.objects.get(Department=teacher.Department)
            return render(request, 'index.html', {'teacher':teacher,'timetable':timetable})
        return render(request, 'index.html', {'teacher':teacher,'timetable':timetable})

    return render(request, 'login.html')

def signout(request):
    return redirect('index')

def attendance(request):
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id)
    assignments = Teacher_Subject_Assignment.objects.filter(TeacherID=id)
    subjects = [assignment.SubjectID for assignment in assignments]
    return render(request, 'attendace.html',{'subjects':subjects,'teacher':teacher})
def main(request):
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id)
    timetable=Timetable.objects.get(Department=teacher.Department,)
    return render(request, 'index.html', {'teacher':teacher,'timetable':timetable})
from django.contrib import messages

def info(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        time_to = request.POST.get('timeto')
        time_from = request.POST.get('timefrom')
        teacher_id = request.GET.get('id')
        subject_id = request.GET.get('Sub')
        id=request.GET.get('id')
        teacher=Teacher.objects.get(Teacherid=id)
        assignments = Teacher_Subject_Assignment.objects.filter(TeacherID=id)
        subjects = [assignment.SubjectID for assignment in assignments]
        sub=Subject.objects.get(SubjectID=subject_id)
        subjectname=Subject.objects.get(SubjectID=subject_id)
        subjectType=subjectname.SubjectType
        subjectname=subjectname.SubjectName
        if subjectType==True:
            students=Student.objects.filter(Year=sub.SubjectYear, Department=sub.SubjectDepartment,Batch=sub.Subjectbatch)
        else:
            students=Student.objects.filter(Year=sub.SubjectYear, Department=sub.SubjectDepartment)
        for student in students:
            is_present = request.POST.get(f'is_present_{student.StudentID}') is not None
            Attendance.objects.create(
                StudentID=student,
                Date=date,
                Timeto=time_to,
                Timefrom=time_from,
                SubjectID=sub,
                SubjectName=subjectname,
                Status=is_present,
            )
        grouped = Attendance.objects.values('SubjectName','Date','Timeto','Timefrom').annotate(student_count=Count('StudentID'))
        return render(request, 'attendace.html',{'subjects':subjects,'teacher':teacher,'grouped':grouped})    

    else:
        teacher_id = request.GET.get('id')
        teacher = Teacher.objects.get(Teacherid=teacher_id)
        subject_id = request.GET.get('Sub')
        subject = Subject.objects.get(SubjectID=subject_id)
        subjectType=subject.SubjectType
        if subjectType==True:
            students=Student.objects.filter(Year=subject.SubjectYear, Department=subject.SubjectDepartment,Batch=subject.Subjectbatch)
        else:
            students=Student.objects.filter(Year=subject.SubjectYear, Department=subject.SubjectDepartment)
        return render(request, 'info_1.html', {'students': students, 'teacher': teacher, 'subject': subject})
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
    id=request.GET.get('id')
    teacher=Teacher.objects.get(Teacherid=id)
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