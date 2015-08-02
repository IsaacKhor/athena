from django.forms import ModelForm, Form, FileField, ChoiceField
from grader.models import Assignment, Grade

class AssgnForm(ModelForm):
    """
    Form for creating a new assignment
    """
    class Meta:
        model = Assignment
        fields = ['title', 'code', 'desc', 'due_date',
            'max_grade', 'weight', 'max_subs']

    def __init__(self, *args, **kwargs):
        super(AssgnForm, self).__init__(*args, **kwargs)
        bootstrapFormControls(self)

class SubmitForm(Form):
    """
    Form for submitting an assignment
    """

    sub_file = FileField(allow_empty_file=False)

    student = ChoiceField()#Testing Only: should be based on login

    def __init__(self, assignment, *args, **kw):
        """
        Associate the form with an assignment
        """

        super(Form, self).__init__(*args, **kw)

        self.fields['student'].choices = map(
            lambda s: (s.id, "%s %s" % (s.first_name, s.last_name)),
            assignment.course.students.all()
        )
        self.assignment = assignment

        bootstrapFormControls(self)

class GradeForm(ModelForm):
    class Meta:
        model = Grade
        fields = ['grader', 'grade', 'comments']

    def __init__(self, sub, *args, **kw):
        """
        Associate the form with a submission
        Grader field is temporary for testing
        """

        super(ModelForm, self).__init__(*args, **kw)

        self.fields['grader'].choices = map(
            lambda u: (u.id, "%s %s" % (u.first_name, u.last_name)),
            sub.assignment.course.instructors.all()
        )
        self.fields['grade'].max_value = sub.assignment.max_grade
        bootstrapFormControls(self)

def bootstrapFormControls(self):
    #bootstrapping form controls
    for field in self.fields:
        self.fields[field].widget.attrs['class'] = 'form-control'
