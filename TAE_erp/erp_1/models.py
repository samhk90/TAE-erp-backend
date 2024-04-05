from django.db import models
import uuid

class Teacher(models.Model):
    Teacherid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    FirstName = models.CharField(max_length=50)
    LastName = models.CharField(max_length=50)
    ContactNumber = models.CharField(max_length=15)
    Email = models.EmailField()
    Department = models.CharField(max_length=50)

class Subject(models.Model):
    SubjectID = models.AutoField(primary_key=True)
    SubjectDepartment= models.CharField(max_length=50, default='DEFAULT_DEPARTMENT')
    SubjectSemester = models.CharField(max_length=50, default='DEFAULT_SEMESTER')
    SubjectYear = models.CharField(max_length=50, default='DEFAULT_YEAR')
    SubjectName = models.CharField(max_length=50)
    SubjectType = models.BooleanField(max_length=50, default=False)
    Subjectbatch = models.CharField(max_length=50, default='DEFAULT_BATCH')
class Teacher_Subject_Assignment(models.Model):
    AssignmentID = models.AutoField(primary_key=True)
    TeacherID = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    SubjectID = models.ForeignKey(Subject, on_delete=models.CASCADE)
class Student(models.Model):
    StudentID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_at=models.DateTimeField(auto_now_add=True)
    PRN = models.CharField(max_length=100, default='DEFAULT_PRN')
    Roll_number = models.CharField(max_length=100,default='DEFAULT_ROLL_NUMBER')
    First_name = models.CharField(max_length=100)
    Last_name = models.CharField(max_length=100)
    Father_name = models.CharField(max_length=100, null=True)
    Father_contact = models.CharField(max_length=15, null=True)
    Mother_name = models.CharField(max_length=100, null=True)
    Mother_contact = models.CharField(max_length=15, null=True)
    Year = models.CharField(max_length=50, default='DEFAULT_CLASS')
    Department = models.CharField(max_length=50, default='DEFAULT_DEPARTMENT')
    division = models.CharField(max_length=50, default='DEFAULT_DIVISION')
    Category = models.CharField(max_length=50, default='DEFAULT_CATEGORY')
    Admission_quota = models.CharField(max_length=50, default='DEFAULT_ADMISSION_QUOTA')
    Email_id = models.EmailField(null=True)
    Mobile_number = models.CharField(max_length=15, null=True)
    Batch= models.CharField(max_length=50, null=True)
class Attendance(models.Model):
    AttendanceID = models.AutoField(primary_key=True)
    StudentID = models.ForeignKey(Student, on_delete=models.CASCADE)
    Date = models.DateField()
    Timeto= models.CharField(max_length=50, default='DEFAULT_TIME')
    Timefrom= models.CharField(max_length=50, default='DEFAULT_TIME')
    SubjectID = models.ForeignKey(Subject, on_delete=models.CASCADE, default=1)
    SubjectName = models.CharField(max_length=50, default='DEFAULT_SUBJECT_NAME')
    Status = models.BooleanField(max_length=50)
class Result(models.Model):
    ResultID = models.AutoField(primary_key=True)
    # StudentID = models.ForeignKey(Student, on_delete=models.CASCADE)
    Subject = models.CharField(max_length=50)
    Marks = models.IntegerField()

class Fees(models.Model):
    FeeID = models.AutoField(primary_key=True)
    StudentID = models.ForeignKey(Student, on_delete=models.CASCADE)
    Total_amount = models.DecimalField(max_digits=7, decimal_places=2)
    Received_amount = models.DecimalField(max_digits=7, decimal_places=2)
    Due_date = models.CharField(max_length=50, default='DEFAULT_DUE_DATE')
    Year = models.CharField(max_length=50, default='DEFAULT_YEAR')
    Status = models.CharField(max_length=50)

class Class(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    number_of_students = models.IntegerField()
    
class ClassTeacherAssignment(models.Model):
    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    assignment_date = models.DateField()
    class_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='class_teachers')
class Notices(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    derpartment = models.CharField(max_length=100 , default='DEFAULT_DEPARTMENT')
    year = models.CharField(max_length=100, default='DEFAULT_YEAR')
    date = models.DateField()
    attachment = models.ImageField(null=True, blank=True)

class Timetable(models.Model):
    timetable_id = models.AutoField(primary_key=True)
    Department = models.CharField(max_length=50)
    year = models.CharField(max_length=50, default='DEFAULT_YEAR')
    division = models.CharField(max_length=50, default='DEFAULT_DIVISION')
    timetable = models.TextField(max_length=1000,default='DEFAULT_TIMETABLE')

