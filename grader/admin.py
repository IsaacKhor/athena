from django.contrib import admin
from .models import *

admin.site.register(Course)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Grade)
admin.site.register(Semester)
