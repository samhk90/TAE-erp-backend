from django.contrib import admin
from .models import Year, Department, Roles, Classes, Subject, Student, Backlog, Alumni, StudentProgression, Attendance, Notices, Fees, Teacher, HOD, TeacherSubjectAssignment, ClassTeacherAssignment, Timetable, Results

admin.site.site_header = ("TAE ERP")
admin.site.site_title = ("TAE ERP Admin")
admin.site.index_title = ("Welcome to TAE ERP Dashboard")

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('YearID', 'YearName')
    search_fields = ('YearName',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('DepartmentID', 'DepartmentName')
    search_fields = ('DepartmentName',)


@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('RoleID', 'RoleName')
    search_fields = ('RoleName',)


@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ('ClassID', 'ClassName', 'DepartmentID', 'YearID')
    search_fields = ('ClassName',)
    list_filter = ('DepartmentID', 'YearID')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('SubjectID', 'SubjectName', 'CurrentClassID', 'SubjectSemester', 'SubjectBatch')
    search_fields = ('SubjectName', 'SubjectBatch')
    list_filter = ('CurrentClassID', 'SubjectSemester', 'SubjectBatch')


@admin.register(Backlog)
class BacklogAdmin(admin.ModelAdmin):
    list_display = ('BacklogID', 'StudentID', 'SubjectID', 'ClassID', 'BacklogDate', 'Status')
    list_filter = ('ClassID', 'Status')
    search_fields = ('StudentID__PRN', 'SubjectID__SubjectName')


@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('AlumniID', 'StudentID', 'GraduationDate', 'LastClassID', 'Email', 'ContactNumber')
    search_fields = ('StudentID__PRN', 'Email', 'ContactNumber')
    list_filter = ('LastClassID',)


@admin.register(StudentProgression)
class StudentProgressionAdmin(admin.ModelAdmin):
    list_display = ('ProgressionID', 'StudentID', 'ClassID', 'StartDate', 'EndDate', 'Status')
    search_fields = ('StudentID__PRN',)
    list_filter = ('ClassID', 'Status')




@admin.register(Notices)
class NoticesAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'ClassID', 'date')
    search_fields = ('title',)
    list_filter = ('ClassID', 'date')


@admin.register(Fees)
class FeesAdmin(admin.ModelAdmin):
    list_display = ('FeeID', 'StudentID', 'TotalAmount', 'ReceivedAmount', 'ClassID', 'Status', 'DueDate')
    search_fields = ('StudentID__PRN',)
    list_filter = ('ClassID', 'Status')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('Teacherid', 'FirstName', 'LastName', 'DepartmentID', 'Email', 'ContactNumber')
    search_fields = ('FirstName', 'LastName', 'Email', 'ContactNumber')
    list_filter = ('DepartmentID',)


@admin.register(HOD)
class HODAdmin(admin.ModelAdmin):
    list_display = ('HODID', 'FirstName', 'LastName', 'DepartmentID', 'Email', 'ContactNumber')
    search_fields = ('FirstName', 'LastName', 'Email', 'ContactNumber')
    list_filter = ('DepartmentID',)


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('AssignmentID', 'TeacherID', 'SubjectID')
    search_fields = ('TeacherID__FirstName', 'TeacherID__LastName', 'SubjectID__SubjectName')
    list_filter = ('TeacherID', 'SubjectID')


@admin.register(ClassTeacherAssignment)
class ClassTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('AssignmentID', 'ClassID', 'TeacherID', 'RoleID')
    search_fields = ('ClassID__ClassName', 'TeacherID__FirstName', 'TeacherID__LastName')
    list_filter = ('ClassID', 'TeacherID', 'RoleID')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('TimetableID', 'ClassID', 'Timetable')
    search_fields = ('ClassID__ClassName',)
    list_filter = ('ClassID',)


@admin.register(Results)
class ResultsAdmin(admin.ModelAdmin):
    list_display = ('ResultID', 'StudentID', 'SubjectID', 'Marks')
    search_fields = ('StudentID__PRN', 'SubjectID__SubjectName')
    list_filter = ('SubjectID',)
