from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
import os

class Semester(models.Model):
    """
    Stores a semester of the school year
    """
    
    #Months the semesters start
    SPRING_MONTH = 1
    SUMMER_MONTH = 5
    FALL_MONTH = 8
    
    #Names of semesters
    TERM_CHOICES = [(FALL_MONTH, 'Fall'), (SPRING_MONTH, 'Spring'), (SUMMER_MONTH, 'Summer')]
    
    year = models.IntegerField()
    term = models.IntegerField(choices=TERM_CHOICES)
    
    def __str__(self):
        return "%s %d" % (dict(self.TERM_CHOICES)[self.term], self.year)
        
    def get_start_date(self):
        return "%d%02d" % (self.year, self.term)
    
    

class Course(models.Model):
    """
    Stores a section of a course for a specific semester
    """

    semester = models.ForeignKey('Semester', blank=True, null=True)
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
        
    def get_directory(self):
        path = os.path.join(settings.SUBMISSION_DIR, 
                            str(self.course.semester), 
                            str(self.course.code), 
                            "Sec.%d" % self.course.section,
                            self.code)
        return path.replace(" ", "_")

class Submission(models.Model):
    """
    Stores a record of a submission for an assignment.
    Actual submission will be stored on filesystem
    """

    #Choices for status of submission
    #SUBMITTED means waiting to be auto graded
    #PASSED and FAILED is based on auto grader
    #GRADED means manually graded (should have Grade entry),
    #assumes it passed auto grader
    CH_SUBMITTED = 0
    CH_PASSED = 1
    CH_FAILED = 2
    CH_GRADED = 3
    STATUS_CHOICES = (
        (CH_SUBMITTED, 'Submitted'),
        (CH_PASSED, 'Passed'),
        (CH_FAILED, 'Failed'),
        (CH_GRADED, 'Graded')
    )

    assignment = models.ForeignKey('Assignment')
    student = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    sub_date = models.DateTimeField(auto_now_add=True)
    
    def get_directory(self):
        path = os.path.join(self.assignment.get_directory(), self.student.username, str(self.sub_date))
        path = path.replace(" ", "_")
        return path
        

class Grade(models.Model):
    """
    Stores a manual grade for a submission
    """

    submission = models.OneToOneField('Submission')
    grader = models.ForeignKey(User)
    grade = models.FloatField()
    date = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True)
