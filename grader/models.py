from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    """
    Stores a section of a course for a specific semester
    """
    
    semester = models.IntegerField()
    code = models.CharField(max_length=10) #ie CSCI160, CSCI120
    section = models.IntegerField()
    title = models.CharField(max_length=128)
    desc = models.TextField(blank=True)
    students = models.ManyToManyField(User, blank=True, related_name='students')
    instructors = models.ManyToManyField(User, related_name='instructors')
    tas = models.ManyToManyField(User, blank=True, related_name='tas')
    
    class Meta:
        unique_together = ('semester', 'code', 'section')
        
    def __str__(self):
        return "%s, %02d, %d" % (self.code, self.section, self.semester)

class Assignment(models.Model):
    """
    Stores an assignment for a course
    Details of assignment should be stored on filesystem
    """
    
    code = models.CharField(max_length=20) #ie HW1, Project2, Midterm, Final
    course = models.ForeignKey('Course')
    title = models.CharField(max_length=128, blank=True, null=True)
    desc = models.TextField(blank=True, verbose_name='description')
    due_date = models.DateTimeField()
    max_grade = models.FloatField(default=100)
    weight = models.FloatField(blank=True, null=True)
    max_subs = models.IntegerField(blank=True, null=True, verbose_name='submission limit')
    
    class Meta:
        unique_together = ('code', 'course')
        
    def __str__(self):
        return "%s %s" % (self.course.code, self.code)

class Submission(models.Model):
    """
    Stores a record of a submission for an assignment.
    Actual submission will be stored on filesystem
    """
    
    #Choices for status of submission
    #SUBMITTED means waiting to be auto graded
    #PASSED and FAILED is based on auto grader
    #GRADED means manually graded (should have Grade entry), assumes it passed auto grader
    CH_SUBMITTED = 0
    CH_PASSED = 1
    CH_FAILED = 2
    CH_GRADED = 3
    STATUS_CHOICES = ( (CH_SUBMITTED, 'Submitted'), (CH_PASSED, 'Passed'), (CH_FAILED, 'Failed'), (CH_GRADED, 'Graded') )
    
    assignment = models.ForeignKey('Assignment')
    student = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    sub_date = models.DateTimeField(auto_now=True, auto_now_add=True)

class Grade(models.Model):
    """
    Stores a manual grade for a submission
    """
    
    submission = models.ForeignKey('Submission', primary_key=True)
    grader = models.ForeignKey(User)
    grade = models.FloatField()
    date = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True)
    
