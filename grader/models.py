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
    Current semester is semester with most recent start date that has already passed
    
    Currently semesters can only be created via admin site
        - May want to further automate this in the future
    """
    
    #Months the semesters start
    SPRING_MONTH = 1
    SUMMER_MONTH = 5
    FALL_MONTH = 8
    
    #Names of semesters
    TERM_CHOICES = [(FALL_MONTH, 'Fall'), (SPRING_MONTH, 'Spring'), (SUMMER_MONTH, 'Summer')]
    
    #########################
    # Start of model fields #
    #########################
    
    #Year and term for semester
    year = models.IntegerField()
    term = models.IntegerField(choices=TERM_CHOICES)
    
    #Stores start and end dates for semester
    #Start date used to determine current semester
    start_date = models.DateField()
    end_date = models.DateField()
    
    #######################
    # End of model fields #
    #######################
    
    #Should not have multiple entries for the same semester
    class Meta:
        unique_together = ('year', 'term')
     
    def __str__(self):
        """
        Prints human readable semester name 
        i.e. Fall 2012, Spring 2016
        """
        return "%s %d" % (dict(self.TERM_CHOICES)[self.term], self.year)
        
    def get_start_date(self):
        """
        Returns semester start date in form yyyydd
        i.e. 201208, 201601
        """
        return "%d%02d" % (self.year, self.term)
    
    @staticmethod
    def get_current():
        """
        Returns the semester with the most recent start date that has already passed
        """
        return Semester.objects.filter(start_date__lte=timezone.now()).order_by('start_date').reverse()[0]
        

class Course(models.Model):
    """
    Stores a section of a course for a specific semester
    """
    
    #########################
    # Start of model fields #
    #########################
    
    #Semester for the course
    semester = models.ForeignKey('Semester', blank=True, null=True)
    
    #Course department + number (i.e. CSCI160, CSCI120)
    code = models.CharField(max_length=10)
    
    #Course section
    section = models.IntegerField()
    
    #Human readable course title
    title = models.CharField(max_length=128)
    
    #Course description
    desc = models.TextField(blank=True)
    
    #Description format 
    #Currently only markdown or plain text - could add more
    desc_format = models.IntegerField(choices=FORMAT_CHOICES, default=TEXT_FORMAT, verbose_name='description format')
    
    #Student, instructor, and TA set for course
    students = models.ManyToManyField(User, blank=True, related_name='students')
    instructors = models.ManyToManyField(User, related_name='instructors')
    tas = models.ManyToManyField(User, blank=True, related_name='tas')
    
    #######################
    # End of model fields #
    #######################
    
    #Semester, code, and section should be unique together
    class Meta:
        unique_together = ('semester', 'code', 'section')
    
    
    def has_student(self, user, allow_superusers=True):
        """
        Returns true if course has student
        """
        return (user.is_superuser and allow_superusers) or len(self.students.filter(id=user.id)) > 0
    
        
    def has_instructor(self, user, allow_superusers=True):
        """
        Returns true if course has instructor
        """
        return (user.is_superuser and allow_superusers) or len(self.instructors.filter(id=user.id)) > 0
    
        
    def has_ta(self, user, allow_superusers=True):
        """
        Returns true if course has TA
        """
        return (user.is_superuser and allow_superusers) or len(self.tas.filter(id=user.id)) > 0
    
        
    def has_user(self, user, allow_superusers=True):
        """
        Returns true if user is a student, instructor, or TA in the course
        """
        return self.has_student(user, allow_superusers) or self.has_ta(user, False) or self.has_instructor(user, False)
        
        
    def get_course_path(self):
        """
        Returns the full path to the directory where course files are stored
        """
        return os.path.join(settings.COURSE_DIR, str(self.id))
        
    def get_course_files(self):
        """
        Returns list of info about the course files in the form (filename, size, date created)
        """
        
        #Make sure course file directory exists
        if not os.path.exists(self.get_course_path()):
            return files
        
        #Add each file in course directory to list
        files = list()
        for f in os.listdir(self.get_course_path()):
            if os.path.isfile(os.path.join(self.get_course_path(), f)):
                info = os.stat(os.path.join(self.get_course_path(), f))
                files.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
            
        return files
    
    
    def get_description(self):
        """
        Returns description in description in specified format
        """
        if self.desc_format == MARKDOWN_FORMAT:
            return markdown.markdown(self.desc, safe_mode='escape') 
        elif self.desc_format == TEXT_FORMAT:
            return html.escape(self.desc)
    
    def __str__(self):
        """
        Returns course title in form of "code, section, semester"
        ex. "CSCI160, 01, Fall 2012"
        """
        return "%s, %02d, %s" % (self.code, self.section, self.semester)


class Assignment(models.Model):
    """
    Stores an assignment for a course
    """
    
    #Options for autograding mode
    #Commented out statuses are not yet implemented
    #Should be implemented once autograder is reliable enough for automatic release
    NO_AUTOGRADE = 0
    MANUAL_REL_AUTOGRADE = 1
    #DEADLINE_REL_AUTOGRADE = 2
    #IMMEDIATE_REL_AUTOGRADE = 3
    AUTOGRADER_CHOICES = ((NO_AUTOGRADE, "No Autograder"),
                          (MANUAL_REL_AUTOGRADE, "Autograde - manually release results"),)
                          #(DEADLINE_REL_AUTOGRADE, "Autograde - release results after deadline"),
                          #(IMMEDIATE_REL_AUTOGRADE, "Autograde - release results immediately"))
                      
    #########################
    # Start of model fields #
    #########################
    
    #Course that the assignment is for
    course = models.ForeignKey('Course')
    
    #Short assignment code (ie HW1, Project2, Midterm, Final)
    code = models.CharField(max_length=20)
    
    #Human readable title for assignment
    title = models.CharField(max_length=128, blank=True, null=True)
    
    #Description and description format for assignment
    desc = models.TextField(blank=True, verbose_name='description')
    desc_format = models.IntegerField(choices=FORMAT_CHOICES, default=TEXT_FORMAT, verbose_name='description format')
    
    #Assignment due date
    due_date = models.DateTimeField()
    
    #If true, will not allow submissions after due date
    enforce_deadline = models.BooleanField(default=True)
    
    #Maximum grade for assignment
    #Currently actual grade can be above (extra credit, for example)
    max_grade = models.FloatField(default=100)
    
    #Maximum number of submissions for this assignment
    max_subs = models.IntegerField(blank=True, null=True, verbose_name='submission limit')
    
    #Assignment will not be visible to students before this date/time
    visible_date = models.DateTimeField(default=timezone.now)
    
    #Determines if assignment can be autograded
    #In the future will also give options for auto-releasing results
    autograde_mode = models.IntegerField(choices=AUTOGRADER_CHOICES, default=NO_AUTOGRADE, verbose_name='autograder options')
    
    #######################
    # End of model fields #
    #######################

    #Assignment code should be unique within course
    #(Can't have multiple "hw1"s)
    class Meta:
        unique_together = ('code', 'course')

    def __str__(self):
        """
        Returns course in format "<Course Code> <Assignment Code>"
        ex. "CSCI160 HW1, CSCI170 Final
        """
        return "%s %s" % (self.course.code, self.code)
    
    
    def is_visible(self):
        """
        Returns true if assignment is visible
        (i.e. if current date/time is after visible date)
        """
        return self.visible_date < timezone.now()
    
    
    def is_past_due(self):
        """
        Returns true if due date is past
        """
        return self.due_date < timezone.now()
    
    
    def get_description(self):
        """
        Returns assignment description in specified format
        """
        if self.desc_format == MARKDOWN_FORMAT:
            return markdown.markdown(self.desc, safe_mode='escape') 
        elif self.desc_format == TEXT_FORMAT:
            return html.escape(self.desc)
        
        
    def get_assignment_path(self):
        """
        Builds path to the directory where files about the assignment are stored
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
        """
        Creates zip file of specified submissions and returns path to it
        If no list of submission IDs provided, will zip all of them
        """
        
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
    #Note status names that appear for students/instructors specified in get_status_student/get_status_instructor
    #These names will still appear in admin site
    CH_SUBMITTED = 0
    CH_AUTOGRADED = 1
    CH_GRADED = 2
    CH_PREVIOUS = 3
    CH_TO_AUTOGRADE = 4
    STATUS_CHOICES = (
        (CH_SUBMITTED, 'Submitted'),
        (CH_AUTOGRADED, 'Autograded'), 
        (CH_GRADED, 'Instructor Graded'),
        (CH_PREVIOUS, 'Past'),
        (CH_TO_AUTOGRADE, 'Submitted'),
    )
    
    #Name of direcories to store extra files
    #These will be subdirectories of "<SUBMISSION_DIR>/<self.id>"
    #SUBMISSION_DIR specified in settings.py
    REPORT_DIR = "report"
    SUPLEMENT_DIR = "suplements"
    
    #########################
    # Start of model fields #
    #########################
    
    #Assignment associated with this submission
    assignment = models.ForeignKey('Assignment')
    
    #Student who submitted this assignment
    student = models.ForeignKey(User)
    
    #Date of submission
    sub_date = models.DateTimeField(auto_now_add=True)
    
    #Status of submisison (see above)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    
    #######################
    # End of model fields #
    #######################
    
    
    def get_status_instructor():
        """
        Returns submission status as instructors/TAs should see it
        Provides different value for every possible status, including if autograder result is released
        """
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
            return "Previous Sub."
            
        elif self.status == self.CH_TO_AUTOGRADE:
            return "Pending"
    
    
    def get_status_student():
        """
        Returns submission status as students should see it
        Hides some information (no seperate statuses for autograding-related things)
        """
        if (self.status == self.CH_GRADED or 
            (self.status == self.CH_AUTOGRADED and self.autograderresult.visible)):
            return "Graded"
            
        elif self.status == self.CH_PREVIOUS:
            return "Previous Sub."
            
        return "Submitted"
        
    
    def set_recent(self):
        """
        Marks all other submissions from this student as previous
        """
        for sub in Submission.objects.filter(assignment=self.assignment, student=self.student).exclude(status=self.CH_PREVIOUS):
            if sub != self:
                sub.status = self.CH_PREVIOUS
                sub.save()
        
        
    def get_directory(self, subdir=None):
        """
        Builds the path to the directory where this submission is stored
        Will be "<SUBMISSION_DIR>/<self.id>", where SUBMISSION_DIR is defined in settings.py
        
        Also allows for optional subdirectory (such as 'report' or 'suplement')
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
        """
        Returns list of files and associated information in "<SUBMISSION_DIR>/<self.id>/suplements"
        Each file is in the form (filename, size, date created)
        These are files uploaded by an instructor or TA about the submission
        """
        files = list()
        
        if not os.path.exists(self.get_directory(subdir=self.SUPLEMENT_DIR)):
            return files
        
        for f in os.listdir(self.get_directory(subdir=self.SUPLEMENT_DIR)):
            if os.path.isfile(os.path.join(self.get_directory(subdir=self.SUPLEMENT_DIR), f)):
                info = os.stat(os.path.join(self.get_directory(subdir=self.SUPLEMENT_DIR), f))
                files.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
        
        return files
        
        
    def get_report_files(self):
        """
        Returns list of files and associated information in "<SUBMISSION_DIR>/<self.id>/report"
        Each file is in the form (filename, size, date created)
        These are files created by the autograder
        """
        file_list = list()
        
        if not os.path.exists(self.get_directory(subdir=self.REPORT_DIR)):
            return None
        
        for path, dirs, files in os.walk(self.get_directory(subdir=self.REPORT_DIR)):
            for f in files:
                info = os.stat(os.path.join(path, f))
                file_list.append((f, int(info[6]), datetime.fromtimestamp(info[9])))
        
        return file_list
        
    def __str__(self):
        """
        Returns submission in form of "<Course code> <Assignment code> <Username> <Timestamp>
        e.x. "CSCI160 HW1 skovaka Dec. 18, 2015, 11:55 p.m."
        """
        return "%s %s %s %s" % (self.assignment.course.code, self.assignment.code, self.student.username, self.sub_date)
        

class Grade(models.Model):
    """
    Stores a instructor/TA submitted grade for a submission
    """
    
    #########################
    # Start of model fields #
    #########################

    #Submission associated with this grade
    submission = models.OneToOneField('Submission')
    
    #Instructor/TA who submitted grade
    grader = models.ForeignKey(User)
    
    #Grade value
    grade = models.FloatField()
    
    #Instructor comments
    comments = models.TextField(blank=True)
    
    #Date/time graded
    date = models.DateTimeField(auto_now=True)
    
    #######################
    # End of model fields #
    #######################
        
    def __str__(self):
        """
        Returns string specifying submission, who graded it, and when
        """
        return "%s (graded by %s at %s)" % (self.submission, self.grader, self.date)
        

class AutograderResult(models.Model):
    """
    Stores a result from the autograder
    """
    
    #########################
    # Start of model fields #
    #########################
    
    #Submission associated with this result
    submission = models.OneToOneField('Submission')
    
    #Date autograder completed
    date = models.DateTimeField(auto_now=True)
    
    #Directory result is stored in
    result_dir = models.TextField()
    
    #Score assigned by autograder
    score = models.FloatField(default=0)
    
    #Will not shown if false
    #Currently must be manually set to true (by instructor)
    #Eventually may be changed automatically after due date
    visible = models.BooleanField(default=False)
    
    #######################
    # End of model fields #
    #######################
        
    def __str__(self):
        """
        Returns string specifying submission and when it was graded
        """
        return "%s (autograded %s)" % (self.submission, self.date)
    

def load_user_groups(user):
    """
    Stores attributes "is_faculty" and "is_student" within user based on groups
    Groups currently must be set via admin site
    
    Returns False if user is not logged in, true otherwise
    """
    if not user.is_authenticated():
        return False
        
    user.is_faculty = len(user.groups.filter(name='faculty')) > 0
    user.is_student = not user.is_faculty

    return True
    
    
def create_user_email(user):
    """
    Generates user email based on username
    Should be run every time a user logs in
    """
    if not user.is_authenticated():
        return False
    
    user.email = "%s@%s" % (user.username, settings.DEFAULT_EMAIL_HOST)
    user.save()
    
    return user.email
    
    
    


