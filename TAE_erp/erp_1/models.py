from django.db import models
import uuid
from django.db import models


class Year(models.Model):
    YearID = models.AutoField(primary_key=True)
    YearName = models.CharField(max_length=255, unique=True)
class Department(models.Model):
    DepartmentID = models.AutoField(primary_key=True)
    DepartmentName = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.YearName

class Roles(models.Model):
    RoleID = models.AutoField(primary_key=True)
    RoleName = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.RoleName

class Classes(models.Model):
    ClassID = models.AutoField(primary_key=True)
    ClassName = models.CharField(max_length=255, unique=True)
    DepartmentID = models.ForeignKey(Department, on_delete=models.CASCADE,default=1)
    YearID = models.ForeignKey(Year, on_delete=models.CASCADE)

    def __str__(self):
        return self.ClassName
class Subject(models.Model):
    SubjectID = models.AutoField(primary_key=True)
    SubjectName = models.CharField(max_length=255)
    CurrentClassID = models.ForeignKey('Classes', on_delete=models.CASCADE,default='none')
    SubjectSemester = models.IntegerField()
    SubjectBatch = models.CharField(max_length=255)
    SubjectYear=models.CharField(max_length=255,default='none')
    SubjectType=models.BooleanField(max_length=50,default=True)
    SubjectDepartment=models.CharField(max_length=255,default='none')
    Subjectdep=models.ForeignKey(Department, on_delete=models.CASCADE,default=4)
    Subjectyr=models.ForeignKey(Year, on_delete=models.CASCADE,default=2)
    def __str__(self):
        return self.SubjectName

class Student(models.Model):
    StudentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    PRN = models.CharField(max_length=255, unique=True)
    FirstName = models.CharField(max_length=255)
    LastName = models.CharField(max_length=255)
    AdharNumber = models.CharField(max_length=255,default='none')
    DOB = models.DateField(default='none')
    Gender=models.CharField(max_length=50,default='none')
    Category=models.CharField(max_length=200,default='none')
    Bloodgrp=models.CharField(max_length=20,default='none')
    tempadd=models.CharField(max_length=255,default='none')
    permenentadd=models.CharField(max_length=255,default='none')
    FatherName = models.CharField(max_length=255, blank=True, null=True)
    FatherContact = models.CharField(max_length=255, blank=True, null=True)
    MotherName = models.CharField(max_length=255, blank=True, null=True)
    MotherContact = models.CharField(max_length=255, blank=True, null=True)
    CurrentClassID = models.ForeignKey('Classes', on_delete=models.CASCADE,default=3)
    Email = models.CharField(max_length=255, unique=True)
    MobileNumber = models.CharField(max_length=255, unique=True)
    RollNumber = models.IntegerField()
    CreatedAt = models.DateTimeField(auto_now_add=True)
    AdmissionQuota = models.CharField(max_length=255,default='none')
    RoleID = models.ForeignKey('Roles', on_delete=models.CASCADE,default=2)
    YearDownStatus = models.BooleanField(default=False)
    batch=models.IntegerField(default=1)

class Backlog(models.Model):
    BacklogID = models.AutoField(primary_key=True)
    StudentID = models.ForeignKey('Student', on_delete=models.CASCADE)
    SubjectID = models.ForeignKey('Subject', on_delete=models.CASCADE)
    ClassID = models.ForeignKey('Classes', on_delete=models.CASCADE)
    BacklogDate = models.DateField()
    Status = models.CharField(
        max_length=50,
        choices=[('Pending', 'Pending'), ('Cleared', 'Cleared')]
    )

    def __str__(self):
        return f"Backlog {self.BacklogID}"

class Alumni(models.Model):
    AlumniID = models.AutoField(primary_key=True)
    StudentID = models.ForeignKey('Student', on_delete=models.CASCADE)
    GraduationDate = models.DateField()
    LastClassID = models.ForeignKey('Classes', on_delete=models.CASCADE)
    Email = models.CharField(max_length=255, unique=True)
    ContactNumber = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Alumni {self.AlumniID}"


class StudentProgression(models.Model):
    ProgressionID = models.AutoField(primary_key=True)
    StudentID = models.ForeignKey('Student', on_delete=models.CASCADE)
    ClassID = models.ForeignKey('Classes', on_delete=models.CASCADE)
    StartDate = models.DateField()
    EndDate = models.DateField()
    Status = models.CharField(
        max_length=50,
        choices=[('Current', 'Current'), ('Completed', 'Completed'), ('Year Down', 'Year Down')]
    )
    YearDownReason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Progression {self.ProgressionID}"
class Attendance(models.Model):
    AttendanceID = models.AutoField(primary_key=True)
    StudentID = models.ForeignKey('Student', on_delete=models.CASCADE)
    SubjectID = models.ForeignKey(Subject, on_delete=models.CASCADE, default=1)
    SubjectName = models.CharField(max_length=50, default='DEFAULT_SUBJECT_NAME')
    ClassID=models.ForeignKey(Classes, on_delete=models.CASCADE, default=3)
    Date = models.DateField()
    Timeto= models.CharField(max_length=50, default='DEFAULT_TIME')
    Timefrom= models.CharField(max_length=50, default='DEFAULT_TIME')
    Status = models.BooleanField(max_length=50)
class Notices(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    ClassID = models.ForeignKey('Classes', on_delete=models.CASCADE)
    date = models.DateField()
    attachment = models.ImageField(null=True, blank=True)
class Fees(models.Model):
    FeeID = models.AutoField(primary_key=True)
    TotalAmount = models.DecimalField(max_digits=10, decimal_places=2)
    ReceivedAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ClassID = models.ForeignKey('Classes', on_delete=models.CASCADE)
    Status = models.CharField(
        max_length=50,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Partial', 'Partial')]
    )
    StudentID = models.ForeignKey('Student', on_delete=models.CASCADE)
    DueDate = models.DateField()

class Teacher(models.Model):
    Teacherid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    FirstName = models.CharField(max_length=255)
    LastName = models.CharField(max_length=255)
    ContactNumber = models.CharField(max_length=255, unique=True)
    Email = models.EmailField(unique=True)
    DepartmentID = models.ForeignKey('Department', on_delete=models.CASCADE)
    RoleID = models.ForeignKey('Roles', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.FirstName} {self.LastName}"


class HOD(models.Model):
    HODID = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=255)
    LastName = models.CharField(max_length=255)
    DepartmentID = models.ForeignKey('Department', on_delete=models.CASCADE)
    ContactNumber = models.CharField(max_length=255, unique=True)
    Email = models.EmailField(unique=True)
    RoleID = models.ForeignKey('Roles', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.FirstName} {self.LastName} - {self.DepartmentID}"

class TeacherSubjectAssignment(models.Model):
    AssignmentID = models.AutoField(primary_key=True)
    TeacherID = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    SubjectID = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def __str__(self):
        return f"Assignment {self.AssignmentID} - {self.TeacherID} - {self.SubjectID}"

from datetime import date

class ClassTeacherAssignment(models.Model):
    AssignmentID = models.AutoField(primary_key=True)
    ClassID = models.ForeignKey('Classes', on_delete=models.CASCADE)
    TeacherID = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    RoleID = models.ForeignKey('Roles', on_delete=models.CASCADE)

    def __str__(self):
        return f"Assignment {self.AssignmentID} - {self.ClassID} - {self.TeacherID}"

class Timetable(models.Model):
    TimetableID = models.AutoField(primary_key=True)
    ClassID = models.ForeignKey('Classes', on_delete=models.CASCADE)
    Timetable = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f"Timetable {self.TimetableID} - {self.DepartmentID} - {self.ClassID} - {self.Division}"

class Results(models.Model):
    ResultID = models.AutoField(primary_key=True)
    SubjectID = models.ForeignKey('Subject', on_delete=models.CASCADE)
    Marks = models.DecimalField(max_digits=10, decimal_places=2)
    StudentID = models.ForeignKey('Student', on_delete=models.CASCADE)

    def __str__(self):
        return f"Result {self.ResultID} - {self.SubjectID} - {self.StudentID} - Marks: {self.Marks}"
