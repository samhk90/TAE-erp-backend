from django.shortcuts import render
from django.shortcuts import render,redirect,get_object_or_404
from erp_1.models import Notices,Timetable,Teacher,Subject,Student,Attendance,TeacherSubjectAssignment,Department,TempTimetable,Classes,ClassTeacherAssignment
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
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseServerError
from django.db import DatabaseError
import logging

logger = logging.getLogger(__name__)

@supabase_login_required
def preacademic(request):
    email = request.session.get('teacher_email')
    teacher = Teacher.objects.get(Email=email)
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
    subject_ids = Timetable.objects.filter(
        Day=day_name,
        SubjectAssignmentID__TeacherID=teacher.Teacherid
    ).values_list('SubjectAssignmentID__SubjectID', flat=True)
    # Get temp slots and their subjects
    temp_slots = TempTimetable.objects.filter(
    Date=today_date,
    ReplacementTeacherID__TeacherID=teacher.Teacherid
).values_list('ReplacementTeacherID__SubjectID', flat=True)

# No need for additional TeacherSubjectAssignment query since we get SubjectID directly
    all_subject_ids = list(subject_ids) + list(temp_slots)
    subjects = Subject.objects.filter(SubjectID__in=all_subject_ids)
    
    subjects = Subject.objects.filter(SubjectID__in=all_subject_ids)
    context={
        'teacher':teacher,
        'subjects':subjects,
    }
    return render(request, 'academics.html', context)

from django.db.models import Count, Q, F

@supabase_login_required
def greenbook(request):
    try:
        email = request.session.get('teacher_email')
        if not email:
            messages.error(request, 'Teacher email not found in session')
            return redirect('login')

        # Optimize by combining queries and using select_related
        try:
            teacher = get_object_or_404(Teacher.objects.select_related(), Email=email)
        except ObjectDoesNotExist:
            messages.error(request, 'Teacher not found')
            logger.error(f'Teacher not found for email: {email}')
            return redirect('login')

        try:
            assignment = get_object_or_404(
                ClassTeacherAssignment.objects.select_related('RoleID', 'ClassID'),
                TeacherID=teacher.Teacherid
            )
        except ObjectDoesNotExist:
            messages.error(request, 'Class teacher assignment not found')
            logger.error(f'Class teacher assignment not found for teacher ID: {teacher.Teacherid}')
            return render(request, 'green.html', {'error': 'No class assignment found'})

        classteacher = assignment.RoleID.RoleName == 'Classteacher'
        
        try:
            # Optimize student query with select_related
            students = Student.objects.filter(
                CurrentClassID=assignment.ClassID
            ).select_related('CurrentClassID').order_by('RollNumber')

            if not students.exists():
                messages.warning(request, 'No students found in this class')
                return render(request, 'green.html', {'no_students': True})

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
                try:
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
                except Exception as e:
                    logger.error(f'Error processing student {student.StudentID}: {str(e)}')
                    continue

            context = {
                'classteacher': classteacher,
                'teacher': teacher,
                'attendance_data': attendance_data,
                'subjects': sorted(subjects_set),
            }
            return render(request, 'green.html', context)

        except DatabaseError as e:
            logger.error(f'Database error: {str(e)}')
            messages.error(request, 'A database error occurred')
            return HttpResponseServerError('A database error occurred')

    except Exception as e:
        logger.error(f'Unexpected error in greenbook view: {str(e)}')
        messages.error(request, 'An unexpected error occurred')
        return HttpResponseServerError('An unexpected error occurred')

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
    try:
        email = request.session.get('teacher_email')
        teacher = get_object_or_404(Teacher.objects.select_related('RoleID', 'DepartmentID'), Email=email)
        role = teacher.RoleID.RoleName
        if role == 'HOD':
            departments = [teacher.DepartmentID]
            print(departments)
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
        return redirect('academics:preacademic')

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


