from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    """
    Stores a section of a course for a specific semester
    """
    
    semester = models.IntegerField()
    code = models.CharField(max_length=10)
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
    Details of assignment may be stored on filesystem
    """
    
    code = models.CharField(max_length=20)
    course = models.ForeignKey('Course')
    title = models.CharField(max_length=128, blank=True, null=True)
    desc = models.TextField(blank=True)
    due_date = models.DateTimeField()
    max_grade = models.FloatField()
    weight = models.FloatField(blank=True, null=True)
    max_subs = models.IntegerField(blank=True, null=True)
    
    class Meta:
        unique_together = ('code', 'course')

class Submission(models.Model):
    """
    Stores a record of a submission for an assignment.
    Actual submission will be stored on filesystem
    """
    
    STATUS_CHOICES = ( (0, 'Submitted'), (1, 'Passed'), (2, 'Failed'), (3, 'Graded') )
    
    assignment = models.ForeignKey('Assignment')
    student = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    sub_date = models.DateTimeField(auto_now=True)

class Grade(models.Model):
    """
    Stores a grade for a submission
    """
    
    submission = models.ForeignKey('Submission', primary_key=True)
    grader = models.ForeignKey(User)
    grade = models.FloatField()
    date = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True)
    
