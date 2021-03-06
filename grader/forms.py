from django.forms import *
from grader.models import *
from  django.contrib.auth.forms import AuthenticationForm
import grader.tasks


class AssgnForm(ModelForm):
    """
    Form for creating a new assignment
    """
    class Meta:
        model = Assignment
        fields = ['title', 'code', 'desc', 'desc_format', 'due_date', 
                  'enforce_deadline', 'max_grade', 'max_subs', 
                  'visible_date', 'autograde_mode', 'autograder_path']

    def __init__(self, *args, **kwargs):
        super(AssgnForm, self).__init__(*args, **kwargs)
        bootstrapFormControls(self)


class CourseForm(ModelForm):
    """
    Form for creating a new course
    """
    class Meta:
        model = Course
        fields = ['semester', 'code', 'section', 'title', 'desc', 'desc_format']
    
    USER_TEXTAREA = Textarea(attrs={'rows': '3'})
    
    instructor_field = CharField(label='Instructors', widget=USER_TEXTAREA, required=False)
    student_field = CharField(label='Students', widget=USER_TEXTAREA, required=False)
    ta_field = CharField(label='TAs', widget=USER_TEXTAREA, required=False)
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        bootstrapFormControls(self)
     

def zip_validator(f):
    pass
        
class SubmitForm(Form):
    """
    Form for submitting an assignment
    """

    sub_file = FileField(label='File', allow_empty_file=False)

    def __init__(self, assignment, user, *args, **kw):
        """
        Associate the form with an assignment
        """
        super(Form, self).__init__(*args, **kw)
        self.assignment = assignment
        self.user = user
        bootstrapFormControls(self)
    
    def save_submission(self):
        """
        Creates a new submission from the form input
        """
        
        #Create a new submission from the form data
        new_sub = Submission(assignment=self.assignment, student=self.user)

        is_autograde = self.assignment.autograde_mode == Assignment.AUTOGRADE

        #Set as user's most recent submission
        new_sub.set_recent()
        
        #Save the submission entry in database
        new_sub.save()
        
        #Make submission directory
        if not os.path.exists(new_sub.get_directory()):
            os.makedirs(new_sub.get_directory())
        
        #Save submission to the filesystem
        filename = os.path.join(new_sub.get_directory(), self.cleaned_data['sub_file'].name)
        with open(filename, 'wb+') as f:
            for chunk in self.cleaned_data['sub_file'].chunks():
                f.write(chunk)

        if is_autograde:
            new_sub.status = Submission.CH_TO_AUTOGRADE
            grader.tasks.autograde_submission(new_sub, filename)

        return new_sub
      
        
class FileUploadForm(Form):
    """
    Form for uploading a file
    """
    
    file_field = FileField(label='Add File', allow_empty_file=False)
    
    def __init__(self, upload_dir, *args, **kw):
        """
        Initialize form and set directory to upload file to
        """
        
        super(Form, self).__init__(*args, **kw)
        self.upload_dir = upload_dir
        #bootstrapFormControls(self)
        
    def save_file(self):
        """
        Saves the uploaded file to the directory specified on initialization
        """
        
        #Make directory
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
        
        #Save submission
        filename = os.path.join(self.upload_dir, self.cleaned_data['file_field'].name)
        with open(filename, 'wb+') as f:
            for chunk in self.cleaned_data['file_field'].chunks():
                f.write(chunk)
        
        
class GradeForm(ModelForm):
    """
    Form to set an assignment grade
    """
    class Meta:
        model = Grade
        fields = ['grade', 'comments']

    def __init__(self, sub, *args, **kw):
        """
        Associate the form with a submission
        """
        super().__init__(*args, **kw)
        self.fields['grade'].max_value = sub.assignment.max_grade
        self.fields['grade'].min_value = 0
        self.instance.submission = sub
        bootstrapFormControls(self)
        
    
        
class LoginForm(AuthenticationForm):
    """
    Login form with bootstrap controls
    """
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        bootstrapFormControls(self)
        

def bootstrapFormControls(self):
    """
    Sets all widgets in a form to use bootstrap controls
    """
    for field in self.fields:
        if type(self.fields[field].widget) != CheckboxInput:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
            
            
            
