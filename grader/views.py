from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.contrib.auth.models import User, Group
import django.contrib.auth as auth

from grader.models import *
from grader.forms import *
from datetime import datetime
from django.db.models import Max

from grader.file_access import get_download

import os
import mimetypes
import re


def login(request):
    """
    Provides user with the login page
    """
    
    #Get username and password from POST data
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        
        #Authenticate username and password
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            
            #User successfully logged in
            if user is not None and user.is_active:
                
                #Load user's email if he/she doesn't have one
                #Should only happen first time user logs in
                if not user.email:
                    create_user_email(user)
                
                #Login and redirect to home page
                auth.login(request, user)
                return HttpResponseRedirect(reverse('grader:home'))
    
    #Create new login form
    else:
        form = LoginForm()
            
    return render(request, 'grader/login.html', {'form': form})
    
    
def logout(request):
    """
    Logs the user out and redirects to the login page
    """
    auth.logout(request)
    return login_redirect(request)
    

def login_redirect(request):
    """
    Returns a redirect response to the login page
    """
    return HttpResponseRedirect(reverse('grader:login'))


def home(request):
    """
    Renders home page
    For now simply shows all courses

    In the future it should show user's enrolled courses or courses they teach, depending on roll
    """
    
    #Make sure user is logged in
    if not load_user_groups(request.user):
        return login_redirect(request)
    
    #Display current semester
    params = {'semester': Semester.get_current()}
    
    #Load student/TA view
    if request.user.is_student:
        params['student_courses'] = request.user.students.filter(semester=params['semester'])
        params['ta_courses'] = request.user.tas.filter(semester=params['semester'])
    
    #Load instructor view
    if request.user.is_faculty:
        params['instructor_courses'] = request.user.instructors.filter(semester=params['semester'])
    
    #Load all courses for superusers
    if request.user.is_superuser:
        params['all_courses'] = Course.objects.all()
        
    
    #Get all the courses and render the template
    courses = Course.objects.all()
    return render(request, 'grader/home.html', params)


def course(request, courseid):
    """
    Renders course page
    Shows course description, assignments, students, instructors, and TA
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated:
        return login_redirect(request)

    #Get the course
    course = Course.objects.get(id=courseid)
    
    params = {'course': course, 'instructor_view': False, 'ta_view': False, 'student_view': False}
    
    #Determine what type of user is viewing the page
    if course.has_instructor(request.user):
        params['instructor_view'] = True
    elif course.has_ta(request.user):
        params['ta_view'] = True
    elif course.has_student(request.user):
        params['student_view'] = True
    else:
        return render(request, 'grader/access_denied.html', params)
    
    #Load all assignments for course
    assignments = course.assignment_set.order_by('due_date').reverse().prefetch_related('submission_set')
    
    #Load student view
    if params.get('student_view'):
        
        #Get student's most recent submission for each assignment
        for a in assignments:
            try:
                a.recent = a.submission_set.exclude(status=Submission.CH_PREVIOUS).get(student=request.user)
            except:
                a.recent = None
    
    #Load instructor/TA view
    else:
        
        #Get number of submissions for each assignment
        for a in assignments:
            a.sub_count = a.submission_set.values('student').distinct().count()
        
        #User add a file - save it and reload page
        if request.method == 'POST':
            params['file_form'] = FileUploadForm(course.get_course_path(), request.POST, request.FILES)
            if params['file_form'].is_valid():
                params['file_form'].save_file()
                return HttpResponseRedirect(reverse('grader:course', args=(course.id,)))
        
        #Load file upload form
        else:
            params['file_form'] = FileUploadForm(course.get_course_path())
    
    #Load assignment list and course files
    params['assignments'] = assignments
    params['files'] = course.get_course_files()
        
    #Render course page
    return render(request, 'grader/course.html', params)


def assignment(request, assgnid):
    """
    Renders assignment page
    Shows what course it's part of, descriptions, submission for, and submissions so far

    In the future it should only show submit form for students,
    only show submissions so far for instructors/TAs.
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated:
        return login_redirect(request)

    #Get the assigment
    assgn = Assignment.objects.get(id=assgnid)
    course = assgn.course
    submissions = assgn.submission_set.all()
    
    params = {'assgn': assgn, 'instructor_view': False, 'ta_view': False, 'student_view': False}
        
    #Load files uploaded for the assignment
    params['files'] = assgn.get_assignment_files()
    
    #Determine what type of user is viewing the page
    if course.has_instructor(request.user):
        params['instructor_view'] = True
    if course.has_ta(request.user):
        params['ta_view'] = True
    if course.has_student(request.user) and assgn.is_visible():
        params['student_view'] = True        
    if not (params.get('instructor_view', False) or params.get('ta_view', False) or params.get('student_view', False)):
        return render(request, 'grader/access_denied.html', params)
    
    #Load info for student
    if params.get('student_view', False):
        
        #Load user's submissions
        params['prev_submissions'] = assgn.submission_set.filter(student=request.user).order_by('sub_date').reverse()

        #Check if student can make new submission
        if (assgn.is_past_due() and assgn.enforce_deadline):
            params['past_due'] = True
        elif (assgn.max_subs and len(params['prev_submissions']) >= assgn.max_subs):
            params['max_subs'] = True
            
        #Student can submit - generate form/save submission
        else:
            
            #Read info from previously submitted submission form
            if request.method == 'POST':
                form = SubmitForm(assgn, request.user, request.POST, request.FILES)
                
                #Vaildate form and save user's submission
                if form.is_valid():
                    new_sub = form.save_submission()
                    
                    #Redirect back to the assignment page
                    return HttpResponseRedirect(reverse('grader:submissions', args=(assgnid,request.user.id)))

            #Create a new submission form
            else:
                form = SubmitForm(assgn, request.user)
            
            params['form'] = form
    
    #Load info for instructors/TAs
    if params.get('instructor_view', False) or params.get('ta_view', False):
        
        #Form data was submitted
        if request.method == 'POST':
            
            #Submissions were selected from table
            if len(request.POST.get('submissions', [])) > 0:
                
                subids = request.POST.getlist('submissions')
                
                #Download selected submissions
                if 'download_many' in request.POST.get('action', []):
                    
                    #Generate CSV file of grades if requested
                    csv_file = None
                    if 'grades' in request.POST.getlist('download_type'):
                        csv_file = course.make_grades_csv(subids)
                        
                        #Return CSV file download if nothing else requested
                        if len(request.POST.getlist('download_type')) == 1:
                            return get_download(csv_file)
                    
                    #Get what needs to be downloaded
                    incl_reports = 'reports' in request.POST.getlist('download_type')
                    incl_subs = 'submissions' in request.POST.getlist('download_type')
                    
                    zipfile = assgn.make_submissions_zip(subids, incl_subs, incl_reports, csv_file)
                    
                    return get_download(zipfile)
                
                #Set AutograderResults on selected submissions to visible
                elif 'show_reports' in request.POST.get('action', []):
                    subs = Submission.objects.filter(pk__in=subids).prefetch_related('autograderresult')
                    for s in subs:
                        s.autograderresult.visible = True
                        s.autograderresult.save()
                    return HttpResponseRedirect(reverse('grader:assignment', args=(assgnid,)))
                
                #Set AutograderResults on selected submissions to not visible
                elif 'hide_reports' in request.POST.get('action', []):
                    subs = Submission.objects.filter(pk__in=subids).prefetch_related('autograderresult')
                    for s in subs:
                        s.autograderresult.visible = False
                        s.autograderresult.save()
                    return HttpResponseRedirect(reverse('grader:assignment', args=(assgnid,)))
            
            #Upload file and associated it with assignment
            if 'add_file' in request.POST.get('action', []):
                params['file_form'] = FileUploadForm(assgn.get_assignment_path(), request.POST, request.FILES)
                if params['file_form'].is_valid():
                    params['file_form'].save_file()
                    return HttpResponseRedirect(reverse('grader:assignment', args=(assgnid,)))
        
        #Create new file uploading form
        else:
            params['file_form'] = FileUploadForm(assgn.get_assignment_path())
        
        #Get all user submissions
        all_subs = assgn.submission_set.order_by('sub_date').reverse()
        
        #Get most recent submission for each student
        params['recent_subs'] = list()
        students_added = set()
        for s in all_subs:
            if not s.student in students_added:
                params['recent_subs'].append(s)
                students_added.add(s.student)
        
        #Check to show options for autograder reports
        params['show_autograde'] = assgn.autograde_mode != Assignment.MANUAL_GRADE
            
    #Render the page
    return render(request, 'grader/assignment.html', params)


def submissions(request, assgnid, userid):
    """
    Renders a page for a student to view their submission
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated:
        return login_redirect(request)

    #Get the submission
    student = User.objects.get(id=userid)
    assgn = Assignment.objects.get(id=assgnid)
    subs = Submission.objects.filter(assignment=assgn, student=student).order_by('sub_date').reverse()
    
    params = {'instructor_view': False, 'ta_view': False, 'student_view': False}
    
    #Determine what type of user is viewing the page
    if assgn.course.has_instructor(request.user):
        params['instructor_view'] = True
    elif assgn.course.has_ta(request.user):
        params['ta_view'] = True
    elif assgn.course.has_student(request.user) and request.user == student and assgn.is_visible():
        params['student_view'] = True        
    else:
        return render(request, 'grader/access_denied.html', {'course': assgn.course})
    
    #Load info most recent and previous submissions
    params['recent'] = subs[0]
    params['prev'] = subs[1:]
    
    #Get status (graded, submitted, etc) for most recent submission
    params['status'] = Submission.STATUS_CHOICES[subs[0].status][1]
    
    #Load suplemental files for most recent submission
    params['suplement_files'] = subs[0].get_suplement_files()
    
    #Load autograder information for most recent submission
    params['autograded'] = hasattr(subs[0], 'autograderresult')
    if params['autograded']:
        
        #Report should be shown if autograde set to visible
        params['show_report'] = subs[0].autograderresult.visible
        
        #Autograder grade should be shown if set to visible and no other grade exists
        params['show_autograde'] = params['show_report'] and Grade.objects.filter(submission=subs[0]).count() == 0
        
        #Load report files if required
        if params.get('instructor_view') or params.get('ta_view') or params['show_report']:
            params['report_files'] = subs[0].get_report_files()
    
    #Load forms for instructors/TAs
    if params.get('instructor_view') or params.get('ta_view'):
        
        #Add file to assignment page
        if request.method == 'POST' and request.POST.get('action', None) == 'add_file':
            params['file_form'] = FileUploadForm(subs[0].get_directory(subdir=Submission.SUPLEMENT_DIR), request.POST, request.FILES)
            if params['file_form'].is_valid():
                params['file_form'].save_file()
                return HttpResponseRedirect(reverse('grader:submissions', args=(assgnid,userid)))
        
        #Create new form to submit files
        else:
            params['file_form'] = FileUploadForm(subs[0].get_directory(subdir=Submission.SUPLEMENT_DIR))                    
        
        #Get the current grade for the submission if it exists
        try:
            grade = Grade.objects.get(submission=subs[0])
        except:
            grade = None
                
        #Update grade
        if request.method == 'POST' and request.POST.get('action', None) == 'grade':
            form = GradeForm(subs[0], request.POST, instance=grade)
            form.instance.grader = request.user

            #Save the grade
            if form.is_valid():
                form.instance.submission.status = Submission.CH_GRADED
                form.instance.submission.save()
                form.save()

                #Redirect back to the submission
                return HttpResponseRedirect(reverse('grader:submissions', args=(assgn.id, student.id)))           
            
        #Generate a new grading form
        else:
            form = GradeForm(subs[0], instance=grade)
        
        params['form'] = form
        
    return render(request, 'grader/submissions.html', params)


def edit_assgn(request, courseid, assgnid=None):
    """
    Renders a page for editting an assignment
    If no assignment ID provided, will generate empty form to create a new assignment
    """

    #Make sure user is logged in
    if not load_user_groups(request.user):
        return login_redirect(request)

    #Get the course associated with assignment
    course = Course.objects.get(id=courseid)
    
    #Make sure user is an instructor or a TA
    if not (course.has_instructor(request.user) or course.has_ta(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})
        
    #Get the assignment if provided
    if assgnid:
        assgn = Assignment.objects.get(id=assgnid)
    else:
        assgn = None
    
    #Get data from previously submitted form
    if request.method == 'POST':
        form = AssgnForm(request.POST, instance=assgn)
        form.instance.course = course

        #Save the assignemnt
        if form.is_valid():
            form.save()
            
            #Redirect to assignment page
            return HttpResponseRedirect(reverse('grader:assignment', args=(form.instance.id,)))

    #Create a new form
    else:
        form = AssgnForm(instance=assgn)
        
    return render(request, 'grader/edit_assgn.html', {'course': course, 'form': form})

DELIM_RE = re.compile(r", *|[\n\r]*")


def edit_course(request, courseid=None):
    """
    Renders a page for editing a course
    If no course ID provided, will generate empty form to create a new course
    """
    #Make sure user is logged in
    if not load_user_groups(request.user):
        return login_redirect(request)
    
    #Load course data if provided
    if courseid:
        course = Course.objects.filter(id=courseid)[0]
        instructor_names = "\n".join(map(lambda u: u.username, course.instructors.all()))
        student_names = "\n".join(map(lambda u: u.username, course.students.all()))
        ta_names = "\n".join(map(lambda u: u.username, course.tas.all()))
        form_data = {'instructor_field': instructor_names, 'student_field': student_names, 'ta_field': ta_names}
    else:
        course = None
        form_data = dict()
        
        
    #Make sure user should be able to edit this course (or the course is just being created)
    if not (request.user.is_superuser                                                            #User must either be a superuser...
            or (course and (course.has_instructor(request.user) or course.has_ta(request.user))) #Or instructor/TA of course being altered...
            or (not course and request.user.is_faculty)):                                        #Or listed as faculty and creating a new course
        return render(request, 'grader/access_denied.html', {'course': course})
    
    #If the form is submitted, get the data
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course, initial=form_data)

        #Save the assignemnt
        if form.is_valid():
            
            #Parse users from form
            instructors = User.objects.filter(username__in=DELIM_RE.split(form.cleaned_data['instructor_field']))
            students = User.objects.filter(username__in=DELIM_RE.split(form.cleaned_data['student_field']))
            tas = User.objects.filter(username__in=DELIM_RE.split(form.cleaned_data['ta_field']))
            
            #Need to save course before adding users
            if not courseid:
                form.save()
            
            #Add users to course
            form.instance.instructors.set(instructors)
            form.instance.instructors.set(students)
            form.instance.instructors.set(tas)
            form.save()
            
            return HttpResponseRedirect(reverse('grader:course', args=(form.instance.id,)))
        
    #Create a new form and render the page
    else:
        form = CourseForm(instance=course, initial=form_data)
        
    return render(request, 'grader/edit_course.html', {'form': form})



