from django.forms import ModelForm, Form, FileField, ChoiceField, CharField, Textarea, BooleanField, MultipleChoiceField, CheckboxSelectMultiple, CheckboxInput
from datetimewidget.widgets import DateTimeWidget
from grader.models import *
from  django.contrib.auth.forms import AuthenticationForm


class AssgnForm(ModelForm):
    """
    Form for creating a new assignment
    """
    class Meta:
        model = Assignment
        fields = ['title', 'code', 'desc', 'desc_format', 'due_date', 'enforce_deadline', 'max_grade', 'max_subs', 'visible_date',]
        
        widgets = {
            'due_date': DateTimeWidget(attrs={'id':"due_date"}, usel10n = True, bootstrap_version=3),
            'visible_date': DateTimeWidget(attrs={'id':"visible_date"}, usel10n = True, bootstrap_version=3)
        }

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
    
    instructor_field = CharField(label='Instructors', widget=USER_TEXTAREA)
    student_field = CharField(label='Students', widget=USER_TEXTAREA)
    ta_field = CharField(label='TAs', widget=USER_TEXTAREA)
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        bootstrapFormControls(self)
     
        
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
        #Create a new submission from the form data
        new_sub = Submission(assignment=self.assignment, student=self.user)
        new_sub.set_recent()
        new_sub.save()
        
        #Make submission directory
        if not os.path.exists(new_sub.get_directory()):
            os.makedirs(new_sub.get_directory())
        
        #Save submission
        filename = os.path.join(new_sub.get_directory(), self.cleaned_data['sub_file'].name)
        with open(filename, 'wb+') as f:
            for chunk in self.cleaned_data['sub_file'].chunks():
                f.write(chunk)
        
        return new_sub
      
        
class FileUploadForm(Form):
    """
    Form for uploading a file
    """
    
    file_field = FileField(label='Add File', allow_empty_file=False)
    
    def __init__(self, upload_dir, *args, **kw):
        super(Form, self).__init__(*args, **kw)
        self.upload_dir = upload_dir
        #bootstrapFormControls(self)
        
    def save_file(self):
        
        #Make directory
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
        
        #Save submission
        filename = os.path.join(self.upload_dir, self.cleaned_data['file_field'].name)
        with open(filename, 'wb+') as f:
            for chunk in self.cleaned_data['file_field'].chunks():
                f.write(chunk)
        
class GradeForm(ModelForm):
    class Meta:
        model = Grade
        fields = ['grade', 'comments']

    def __init__(self, sub, *args, **kw):
        """
        Associate the form with a submission
        """
        super().__init__(*args, **kw)
        self.fields['grade'].max_value = sub.assignment.max_grade
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
    #bootstrapping form controls
    for field in self.fields:
        if type(self.fields[field].widget) != CheckboxInput:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
            
            
            
