from django.shortcuts import render
from django.shortcuts import render,redirect,get_object_or_404
from erp_1.models import Notices,Timetable,Teacher,Subject,Student,Attendance,TeacherSubjectAssignment,Department,Year,Classes,ClassTeacherAssignment
from supabase import create_client, Client,SupabaseAuthClient
from django.core.serializers import serialize
from django.shortcuts import render
from erp_1.decorators import supabase_login_required  # Adjust the import path accordingly
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from erp_1.models import Teacher, ClassTeacherAssignment, Student, Attendance,Slots
from datetime import date

from datetime import timedelta
from django.utils import timezone
from collections import defaultdict
from django.db.models import Case, When, IntegerField, FloatField
from django.shortcuts import redirect
from django.http import HttpResponse
import supabase
@supabase_login_required
def preacademic(request):
    email = request.session.get('teacher_email')
    teacher = Teacher.objects.get(Email=email)

    # Use `.filter()` to avoid exceptions and check the role directly in the query
    classteacher = ClassTeacherAssignment.objects.filter(
        TeacherID=teacher.Teacherid, RoleID__RoleName='Classteacher'
    ).exists()

    context = {
        'teacher': teacher,
        'classteacher': classteacher,
    }
    return render(request, 'preacademic.html', context)

@supabase_login_required
def pre_attendance(request):
    email = request.session.get('teacher_email')
    teacher = get_object_or_404(Teacher, Email=email)
    today_date = date.today()
    day_name = today_date.strftime("%A")
    day_name = 'Thursday' 
    subject_ids = Timetable.objects.filter(
        Day=day_name,
        SubjectAssignmentID__TeacherID=teacher.Teacherid
    ).values_list('SubjectAssignmentID__SubjectID', flat=True)
    subjects = Subject.objects.filter(SubjectID__in=subject_ids)
    context={
        'teacher':teacher,
        'subjects':subjects,
    }
    return render(request, 'academics.html', context)

from django.db.models import Count, Q, F

@supabase_login_required
def greenbook(request):
    email = request.session.get('teacher_email')
    # Optimize by combining queries and using select_related
    teacher = get_object_or_404(Teacher.objects.select_related(), Email=email)
    assignment = get_object_or_404(
        ClassTeacherAssignment.objects.select_related('RoleID', 'ClassID'),
        TeacherID=teacher.Teacherid
    )
    classteacher = assignment.RoleID.RoleName == 'Classteacher'
    
    # Optimize student query with select_related
    students = Student.objects.filter(
        CurrentClassID=assignment.ClassID
    ).select_related('CurrentClassID').order_by('RollNumber')
    
    # Optimize attendance query by using prefetch_related and annotations
    attendance_records = (
        Attendance.objects.filter(
            StudentID__in=students.values_list('StudentID', flat=True)
        ).select_related('StudentID', 'SubjectID')
        .values('StudentID', 'SubjectID', 'SubjectName')
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

    # Use dictionary for O(1) lookups instead of list operations
    attendance_by_student = defaultdict(list)
    subjects_set = set()
    
    for record in attendance_records:
        subjects_set.add(record['SubjectName'])
        attendance_by_student[record['StudentID']].append(record)

    attendance_data = []
    for student in students:
        student_records = attendance_by_student.get(student.StudentID, [])
        if student_records:
            total_attended = sum(rec['attended_count'] for rec in student_records)
            total_conducted = sum(rec['total_lectures'] for rec in student_records)
            average_percentage = (total_attended / total_conducted * 100) if total_conducted > 0 else 0
        else:
            total_attended = 0
            average_percentage = 0

        attendance_data.append({
            'student': {
                'RollNo': student.RollNumber,
                'FirstName': student.FirstName,
                'LastName': student.LastName,
            },
            'attendance': student_records,
            'total_attended': total_attended,
            'average_percentage': average_percentage,
        })

    context = {
        'classteacher': classteacher,
        'teacher': teacher,
        'attendance_data': attendance_data,
        'subjects': sorted(subjects_set),
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
        date1 = date.today()
        slot=request.POST.get('slot')
        slot=Slots.objects.get(Slotid=slot)
        print(slot)
        time_to = request.POST.get('start')
        print(time_to)
        time_from = request.POST.get('end')
        print(time_from)
        subject = get_object_or_404(Subject, SubjectID=subject_id)
        classid=Classes.objects.get(ClassID=selected_class)
        existing_attendance = Attendance.objects.filter(
            Date=date1,
            SlotID=slot,
            SubjectID=subject
        ).exists()

        if existing_attendance:
            # If attendance already exists, show an error message
            messages.error(request, 'Attendance already exists.')
            print('bc dekh ke kr')
            return redirect('academics:pre_attendance')  # Redirect back to the same form with the error message

        if subject.SubjectType == False and batch:
            batch = int(batch)  # Ensure batch is an integer if needed
            students = Student.objects.filter(CurrentClassID=selected_class, batch=batch).order_by('RollNumber')
        else:
            students = Student.objects.filter(CurrentClassID=selected_class).order_by('RollNumber')
        
        attendance_records = []
        for student in students:
            is_present = request.POST.get(f'is_present_{student.StudentID}') == 'on'
            attendance_records.append(Attendance(
                StudentID=student,
                Date=date1,
                Timeto=str(time_to),
                Timefrom=str(time_from),
                SubjectID=subject,
                SubjectName=subject.SubjectName,
                SlotID=slot,
                Status=is_present,
                ClassID=classid
            ))

        Attendance.objects.bulk_create(attendance_records)
        messages.success(request, 'Attendance has been marked successfully.')
        return redirect('academics:pre_attendance')

    # If GET request or form not submitted
    subject = get_object_or_404(Subject, SubjectID=subject_id)
    today_date = date.today()
    day_name = today_date.strftime("%A")
    day_name = 'Tuesday'
    slot = Timetable.objects.filter(
    SubjectAssignmentID__SubjectID=subject_id, 
    Day=day_name
).values_list('SlotID', flat=True).first()
    slot=Slots.objects.get(Slotid=slot)
    print(slot)
    if batch:
        batch = int(batch)  # Ensure batch is an integer if needed
        students = Student.objects.filter(CurrentClassID=selected_class, batch=batch).order_by('RollNumber')
    else:
        students = Student.objects.filter(CurrentClassID=selected_class).order_by('RollNumber')
    
    subjecttype = subject.SubjectType
    role1 = ClassTeacherAssignment.objects.filter(TeacherID=teacher.Teacherid).first()
    is_classteacher = role1 and role1.RoleID.RoleName == 'Classteacher'
    selected_class = Classes.objects.get(ClassID=selected_class)
    
    context = {
        'date':today_date,
        'subjecttype': subjecttype,
        'students': students,
        'teacher': teacher,
        'subject': subject,
        'selected_class': selected_class,
        'batch': batch,
        'slot':slot,
        'is_classteacher': is_classteacher
    }
    return render(request, 'attendance_form.html', context)

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

    timetable = defaultdict(lambda: defaultdict(list))  
    slot_list = set()  
    
    for entry in timetable_entries:
        timetable[entry.Day][entry.SlotID].append(entry.SubjectAssignmentID)
        slot_list.add(entry.SlotID)  
    processed_timetable = {
        day: {
            slot: assignments for slot, assignments in slots.items()
        } for day, slots in timetable.items()
    }
    
    context = {
        'timetable': processed_timetable.items(),
        'classes': classes,
        'selected_timetable_type': selected_timetable_type,
        'slot_list': slot_list,
        'teacher': teacher
    }
    
    return render(request, 'timetable.html', context)

@supabase_login_required
def report(request):
    email = request.session.get('teacher_email')
    # Optimize initial queries with select_related
    teacher = get_object_or_404(Teacher.objects.select_related('DepartmentID'), Email=email)
    
    # Optimize assignments query with select_related
    assignments = TeacherSubjectAssignment.objects.filter(
        TeacherID=teacher.Teacherid
    ).select_related('SubjectID', 'SubjectID__CurrentClassID')
    
    # Use values_list for better performance
    subject_ids = assignments.values_list('SubjectID__SubjectID', flat=True)
    
    # Optimize subject and class queries
    subjects = Subject.objects.filter(
        SubjectID__in=subject_ids
    ).select_related('CurrentClassID')
    
    class_ids = subjects.values_list('CurrentClassID', flat=True).distinct()
    assigned_classes = Classes.objects.filter(ClassID__in=class_ids)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        selected_subject = request.POST.get('subject')
        selected_class_id = request.POST.get('class')
        
        # Optimize by combining queries
        selected_class = get_object_or_404(Classes.objects.select_related(), ClassID=selected_class_id)
        students = Student.objects.filter(
            CurrentClassID=selected_class
        ).select_related('CurrentClassID').order_by('RollNumber')

        attendance_data = []
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Optimize attendance query by using prefetch_related and annotations
            attendance_records = Attendance.objects.filter(
                StudentID__in=students.values_list('StudentID', flat=True),
                SubjectID=selected_subject,
                Date__range=(start_date, end_date)
            ).values(
                'StudentID'
            ).annotate(
                attended_count=Count('AttendanceID', filter=Q(Status=True)),
                total_lectures=Count('AttendanceID'),
                attendance_percentage=Case(
                    When(total_lectures__gt=0, 
                         then=100.0 * Count('AttendanceID', filter=Q(Status=True)) / Count('AttendanceID')),
                    default=0.0,
                    output_field=FloatField(),
                )
            )
            
            # Create lookup dictionary for O(1) access
            attendance_by_student = {
                record['StudentID']: record for record in attendance_records
            }
            
            for student in students:
                record = attendance_by_student.get(student.StudentID, {
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

    # Initial render context
    context = {
        'teacher': teacher,
        'subjects': subjects,
        'classes': assigned_classes,
    }
    return render(request, 'attendance_report.html', context)

import csv
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

from django.http import HttpResponse
import json

from datetime import date
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

@supabase_login_required
def pretest(request):
    email = request.session.get('teacher_email')
    # Optimize by using select_related and combining queries
    teacher = get_object_or_404(Teacher.objects.select_related('DepartmentID'), Email=email)
    
    # Use a constant for the day since it's hardcoded anyway
    day_name = 'Tuesday'
    
    # Optimize timetable query by using select_related and values_list
    subject_ids = Timetable.objects.filter(
        Day=day_name,
        SubjectAssignmentID__TeacherID=teacher.Teacherid
    ).select_related(
        'SubjectAssignmentID__SubjectID'
    ).values_list(
        'SubjectAssignmentID__SubjectID', 
        flat=True
    ).distinct()
    
    # Optimize subjects query with select_related
    subjects = Subject.objects.filter(
        SubjectID__in=subject_ids
    ).select_related('CurrentClassID')
    
    return render(request, 'test.html', {
        'timetables1': list(subject_ids),
    })
