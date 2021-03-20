from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from zipfile import ZipFile
from django.utils import timezone
import os
import markdown
import html


TEXT_FORMAT = 0
MARKDOWN_FORMAT = 1
FORMAT_CHOICES = ((TEXT_FORMAT, 'Plain Text'), (MARKDOWN_FORMAT, 'Markdown'))

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
    start_date = models.DateField()
    end_date = models.DateField()
     
    def __str__(self):
        return "%s %d" % (dict(self.TERM_CHOICES)[self.term], self.year)
        
    def get_start_date(self):
        return "%d%02d" % (self.year, self.term)
    
    @staticmethod
    def get_current():
        return Semester.objects.filter(start_date__lte=timezone.now()).order_by('start_date')[0]
        

class Course(models.Model):
    """
    Stores a section of a course for a specific semester
    """

    semester = models.ForeignKey('Semester', blank=True, null=True)
    code = models.CharField(max_length=10) #ie CSCI160, CSCI120
    section = models.IntegerField()
    title = models.CharField(max_length=128)
    desc = models.TextField(blank=True)
    desc_format = models.IntegerField(choices=FORMAT_CHOICES, default=TEXT_FORMAT, verbose_name='description format')
    students = models.ManyToManyField(User, blank=True, related_name='students')
    instructors = models.ManyToManyField(User, related_name='instructors')
    tas = models.ManyToManyField(User, blank=True, related_name='tas')
    
    class Meta:
        unique_together = ('semester', 'code', 'section')
    
    def has_student(self, user, allow_superusers=True):
        return (user.is_superuser and allow_superusers) or len(self.students.filter(id=user.id)) > 0
        
    def has_instructor(self, user, allow_superusers=True):
        return (user.is_superuser and allow_superusers) or len(self.instructors.filter(id=user.id)) > 0
        
    def has_ta(self, user, allow_superusers=True):
        return (user.is_superuser and allow_superusers) or len(self.tas.filter(id=user.id)) > 0
        
    def has_user(self, user, allow_superusers=True):
        return self.has_student(user, allow_superusers) or self.has_ta(user, False) or self.has_instructor(user, False)
        
    def get_course_path(self):
        return os.path.join(settings.COURSE_DIR, str(self.id))
        
    def get_course_files(self):
        """
        Returns list of info about the course files in the form (filename, size, date created)
        """
        files = list()
        
        #Make sure course file directory exists
        if not os.path.exists(self.get_course_path()):
            return files
            
        for f in os.listdir(self.get_course_path()):
            if os.path.isfile(os.path.join(self.get_course_path(), f)):
                info = os.stat(os.path.join(self.get_course_path(), f))
                files.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
            
        return files
    
    def get_description(self):
        if self.desc_format == MARKDOWN_FORMAT:
            return markdown.markdown(self.desc, safe_mode='escape') 
        elif self.desc_format == TEXT_FORMAT:
            return html.escape(self.desc)
    
    def __str__(self):
        return "%s, %02d, %s" % (self.code, self.section, self.semester)

class Assignment(models.Model):
    """
    Stores an assignment for a course
    Details of assignment should be stored on filesystem
    """
    
    NO_AUTOGRADE = 0
    MANUAL_REL_AUTOGRADE = 1
    DEADLINE_REL_AUTOGRADE = 2
    IMMEDIATE_REL_AUTOGRADE = 3
    
    AUTOGRADER_CHOICES = ((NO_AUTOGRADE, "No Autograder"),
                          (MANUAL_REL_AUTOGRADE, "Autograde - manually release results"),)
                          #(DEADLINE_REL_AUTOGRADE, "Autograde - release results after deadline"),
                          #(IMMEDIATE_REL_AUTOGRADE, "Autograde - release results immediately"))
                      
    
    code = models.CharField(max_length=20) #ie HW1, Project2, Midterm, Final
    course = models.ForeignKey('Course')
    title = models.CharField(max_length=128, blank=True, null=True)
    desc = models.TextField(blank=True, verbose_name='description')
    due_date = models.DateTimeField()
    max_grade = models.FloatField(default=100)
    max_subs = models.IntegerField(blank=True, null=True, verbose_name='submission limit')
    enforce_deadline = models.BooleanField(default=True)
    visible_date = models.DateTimeField(default=timezone.now)
    desc_format = models.IntegerField(choices=FORMAT_CHOICES, default=TEXT_FORMAT, verbose_name='description format')
    autograde_mode = models.IntegerField(choices=AUTOGRADER_CHOICES, default=NO_AUTOGRADE, verbose_name='autograder options')


    class Meta:
        unique_together = ('code', 'course')

    def __str__(self):
        return "%s %s" % (self.course.code, self.code)
    
    def is_visible(self):
        return self.visible_date < timezone.now()
    
    def is_past_due(self):
        return self.due_date < timezone.now()
    
    def get_description(self):
        if self.desc_format == MARKDOWN_FORMAT:
            return markdown.markdown(self.desc, safe_mode='escape') 
        elif self.desc_format == TEXT_FORMAT:
            return html.escape(self.desc)
        
    def get_assignment_path(self):
        """
        Builds path to the directory where files about the assignment are
        """
        return os.path.join(self.course.get_course_path(), str(self.id))
        
    def get_assignment_files(self):
        """
        Returns list of info about the assignment files in the form (filename, size, date created)
        """
        files = list()
        
        #Make sure assignment file directory exists
        if not os.path.exists(self.get_assignment_path()):
            return files
            
        for f in os.listdir(self.get_assignment_path()):
            if os.path.isfile(os.path.join(self.get_assignment_path(), f)):
                info = os.stat(os.path.join(self.get_assignment_path(), f))
                files.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
            
        return files
    
    def get_directory(self):
        """
        Builds the path to the directory where all the submissions are stored
        """
        path = os.path.join(settings.SUBMISSION_DIR, 
                            str(self.course.semester), 
                            str(self.course.code), 
                            "Sec.%d" % self.course.section,
                            self.code)
        return path.replace(" ", "_")
    
    def make_submissions_zip(self, subids=None):
        
        #Initial filename
        zip_path = os.path.join(settings.TEMP_DIR, "%s_%s_subs.zip" % (self.course.code, self.code))
        
        #Find new tmp filename
        i = 1
        while os.path.exists(zip_path):
            zip_path = os.path.join(settings.TEMP_DIR, "%s_%s_subs_%d.zip" % (self.course.code, self.code, i))
            i += 1
        
        #Open file
        zfile = ZipFile(zip_path, "w")
        
        #Load submissions to put into zipfile
        if subids:
            submissions = self.submission_set.filter(id__in=subids)
        else:
            submissions = self.submission_set.all()
        
        #Write all submissions to the zip file
        for sub in submissions:
            sub_path = sub.get_directory()
            sub_name = sub.get_filename()
            zfile.write(os.path.join(sub_path, sub_name), os.path.join(sub.student.username, sub_name))
        zfile.close()
        
        return zip_path

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
    CH_AUTOGRADED = 1
    CH_GRADED = 2
    CH_PREVIOUS = 3
    CH_TO_AUTOGRADE = 4
    STATUS_CHOICES = (
        (CH_SUBMITTED, 'Submitted'),
        (CH_AUTOGRADED, 'Submitted'), #Should later be labeled something else - hidden for now
        (CH_GRADED, 'Instructor Graded'),
        (CH_PREVIOUS, 'Past'),
        (CH_TO_AUTOGRADE, 'Submitted'),
    )
    
    REPORT_DIR = "report"
    SUPLEMENT_DIR = "suplements"

    assignment = models.ForeignKey('Assignment')
    student = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    sub_date = models.DateTimeField(auto_now_add=True)
    
    def get_status_instructor():
        if self.status == self.CH_SUBMITTED:
            return "Submitted"
            
        elif self.status == self.CH_AUTOGRADED:
            if self.autograderresult.visible:
                return "Autograded (released)"
            else:
                return "Autograded (hidden)"
            
        elif self.status == self.CH_GRADED:
            return "Graded"
            
        elif self.status == self.CH_PREVIOUS:
            return "Previous sub"
            
        elif self.status == self.CH_TO_AUTOGRADE:
            return "Pending"
    
    testthing = "ehllo"
    def get_status_student():
        if (self.status == self.CH_GRADED or 
            (self.status == self.CH_AUTOGRADED and self.autograderresult.visible)):
            return "Graded"
            
        elif self.status == self.CH_PREVIOUS:
            return "Previous sub"
            
        else:
            return "Submitted"
        
        return "NOTHING"
        
    
    def set_recent(self):
        """
        Marks all other submissions from this assignment and student as previous
        """
        for sub in Submission.objects.filter(assignment=self.assignment, student=self.student).exclude(status=self.CH_PREVIOUS):
            if sub != self:
                sub.status = self.CH_PREVIOUS
                sub.save()
        
    def get_directory(self, subdir=None):
        """
        Builds the path to the directory where this submission is stored
        """
        path = os.path.join(settings.SUBMISSION_DIR, str(self.id))
        
        if subdir:
            path = os.path.join(path, subdir)
            
        return path
        
    def get_filename(self):
        """
        Returns the filename of the submission. Use get_directory() to get the path to this file.
        """
                    
        for f in os.listdir(self.get_directory()):
            if os.path.isfile(os.path.join(self.get_directory(), f)):
                return f
            
        return None
        
    def get_suplement_files(self):
        files = list()
        
        if not os.path.exists(self.get_directory(subdir=self.SUPLEMENT_DIR)):
            return files
        
        for f in os.listdir(self.get_directory(subdir=self.SUPLEMENT_DIR)):
            if os.path.isfile(os.path.join(self.get_directory(subdir=self.SUPLEMENT_DIR), f)):
                info = os.stat(os.path.join(self.get_directory(subdir=self.SUPLEMENT_DIR), f))
                files.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
        
        return files
        
    def get_report_files(self):
        file_list = list()
        
        if not os.path.exists(self.get_directory(subdir=self.REPORT_DIR)):
            return None
        
        for path, dirs, files in os.walk(self.get_directory(subdir=self.REPORT_DIR)):
            for f in files:
                info = os.stat(os.path.join(path, f))
                file_list.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
        
        return file_list
        
    def get_assignment_files(self):
        """
        Returns list of info about the assignment files in the form (filename, size, date created)
        """
        files = list()
        
        #Make sure assignment file directory exists
        if not os.path.exists(self.get_assignment_path()):
            return files
            
        for f in os.listdir(self.get_assignment_path()):
            if os.path.isfile(os.path.join(self.get_assignment_path(), f)):
                info = os.stat(os.path.join(self.get_assignment_path(), f))
                files.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
            
        return files
        
    def __str__(self):
        return "%s %s %s %s" % (self.assignment.course.code, self.assignment.code, self.student.username, self.sub_date)
        

class Grade(models.Model):
    """
    Stores a manual grade for a submission
    """

    submission = models.OneToOneField('Submission')
    grader = models.ForeignKey(User)
    grade = models.FloatField()
    date = models.DateTimeField(auto_now=True)
    comments = models.TextField(blank=True)
        
    def __str__(self):
        return str(self.submission)
        

class AutograderResult(models.Model):
    """
    Stores a result from the auto grader
    """

    submission = models.OneToOneField('Submission')
    date = models.DateTimeField(auto_now=True)
    result_dir = models.TextField()
    score = models.FloatField(default=0)
    visible = models.BooleanField(default=False)
        
    def __str__(self):
        return "yes"
    

def load_user_groups(user):
    if not user.is_authenticated():
        return False
        
    user.is_faculty = len(user.groups.filter(name='faculty')) > 0
    #user.is_student = len(user.groups.filter(name='students')) > 0
    user.is_student = not user.is_faculty

    return True
    
def create_user_email(user):
    if not user.is_authenticated():
        return False
    
    user.email = "%s@%s" % (user.username, settings.DEFAULT_EMAIL_HOST)
    user.save()
    
    return user.email
    
    
    


