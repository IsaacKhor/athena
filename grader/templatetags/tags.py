from django import template
from grader.models import Submission

register = template.Library()

@register.filter
def submission_status(sub, is_student):
        
    if sub.status == sub.CH_AUTOGRADED and not is_student:
        if hasattr(sub, "autograderresult") and sub.autograderresult.visible:
            return "Autograded (visible)"
        else:
            return "Autograded (hidden)"
        
    elif (sub.status == sub.CH_GRADED or 
          (sub.status == sub.CH_AUTOGRADED and sub.autograderresult.visible)):
            return "Graded"
        
    elif sub.status == sub.CH_PREVIOUS:
        return "Previous sub"
        
    elif sub.status == sub.CH_TO_AUTOGRADE and is_student:
        return "Pending"
    
    else:
        return "Submitted"
        
register.filter('submission_status', submission_status)

