from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.models import User, Group
import django.contrib.auth as auth
from grader.models import *
from grader.forms import *
from datetime import datetime
from django.db.models import Max

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
                
                if not user.email:
                    create_user_email(user)
                    
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
    
    params = {'semester': Semester.get_current()}
    
    
    if request.user.is_student:
        params['student_courses'] = request.user.students.filter(semester=params['semester'])
        params['ta_courses'] = request.user.tas.filter(semester=params['semester'])
    
    if request.user.is_faculty:
        params['instructor_courses'] = request.user.instructors.filter(semester=params['semester'])
    
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
    if not request.user.is_authenticated():
        return login_redirect(request)

    #Get the course
    course = Course.objects.get(id=courseid)
    
    params = {'course': course}
    
    #Determine what type of user is viewing the page
    if course.has_instructor(request.user):
        params['instructor_view'] = True
    elif course.has_ta(request.user):
        params['ta_view'] = True
    elif course.has_student(request.user):
        params['student_view'] = True
    else:
        return render(request, 'grader/access_denied.html', params)
    
    
    assignments = course.assignment_set.order_by('due_date').reverse().prefetch_related('submission_set')
    
    if params.get('student_view'):
        for a in assignments:
            subs = a.submission_set.filter(student=request.user).order_by('sub_date').reverse()
            if subs.count() > 0:
                a.recent = subs[0]
                a.status = Submission.STATUS_CHOICES[subs[0].status][1]
            else:
                a.recent = None
    else:
        
        params['time_now'] = datetime.now()
        
        for a in assignments:
            a.sub_count = a.submission_set.values('student').distinct().count()
        
        if request.method == 'POST':
            params['file_form'] = FileUploadForm(course.get_course_path(), request.POST, request.FILES)
            if params['file_form'].is_valid():
                params['file_form'].save_file()
                return HttpResponseRedirect(reverse('grader:course', args=(course.id,)))
        else:
            params['file_form'] = FileUploadForm(course.get_course_path())
    
    params['assignments'] = assignments
    params['files'] = course.get_course_files()
        
    
    return render(request, 'grader/course.html', params)


def assignment(request, assgnid):
    """
    Renders assignment page
    Shows what course it's part of, descriptions, submission for, and submissions so far

    In the future it should only show submit form for students,
    only show submissions so far for instructors/TAs.
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)

    #Get the assigment
    assgn = Assignment.objects.get(id=assgnid)
    course = assgn.course
    submissions = assgn.submission_set.all()
    
    params = {'assgn': assgn}
    
    #Determine what type of user is viewing the page
    if course.has_instructor(request.user):
        params['instructor_view'] = True
    elif course.has_ta(request.user):
        params['ta_view'] = True
    elif course.has_student(request.user) and assgn.is_visible():
        params['student_view'] = True        
    else:
        return render(request, 'grader/access_denied.html', params)
    
    #Load submissions into parameters
    if params.get('student_view', False):
        params['prev_submissions'] = assgn.submission_set.filter(student=request.user).order_by('sub_date').reverse()

        #Make sure user should be able to submit
        if (assgn.is_past_due() and assgn.enforce_deadline):
            params['past_due'] = True
        elif (assgn.max_subs and len(params['prev_submissions']) >= assgn.max_subs):
            params['max_subs'] = True
            
        else:
            #Get data from a submission
            if request.method == 'POST':
                form = SubmitForm(assgn, request.user, request.POST, request.FILES)

                if form.is_valid():

                    new_sub = form.save_submission()
                    
                    #Redirect back to the assignment page
                    return HttpResponseRedirect(reverse('grader:submissions', args=(assgnid,request.user.id)))

            #Create a new submission form
            else:
                form = SubmitForm(assgn, request.user)
            
            params['form'] = form
    
    #Load each student's most recent submission
    else:
        
        if request.method == 'POST':
            if len(request.POST.get('submissions', [])) > 0:
                print(request.POST.getlist('submissions'))
                if 'download_many' in request.POST.get('action', []):
                    zipfile = assgn.make_submissions_zip(request.POST.getlist('submissions'))
                    return get_download(zipfile)
                    
            elif not 'action' in request.POST:
                params['file_form'] = FileUploadForm(assgn.get_assignment_path(), request.POST, request.FILES)
                if params['file_form'].is_valid():
                    params['file_form'].save_file()
                    return HttpResponseRedirect(reverse('grader:assignment', args=(assgnid,)))
                    
        else:
            params['file_form'] = FileUploadForm(assgn.get_assignment_path())
        
        params['files'] = assgn.get_assignment_files()
        
        all_subs = assgn.submission_set.order_by('sub_date').reverse()
        params['recent_subs'] = list()
        students_added = set()
        for s in all_subs:
            if not s.student in students_added:
                params['recent_subs'].append(s)
                students_added.add(s.student)

    #Render the page
    return render(request, 'grader/assignment.html', params)


def submissions(request, assgnid, userid):
    """
    Renders a page for a student to view their submission
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)

    #Get the submission
    student = User.objects.get(id=userid)
    assgn = Assignment.objects.get(id=assgnid)
    subs = Submission.objects.filter(assignment=assgn, student=student).order_by('sub_date').reverse()
    
    params = dict()
    
    #Determine what type of user is viewing the page
    if assgn.course.has_instructor(request.user):
        params['instructor_view'] = True
    elif assgn.course.has_ta(request.user):
        params['ta_view'] = True
    elif assgn.course.has_student(request.user) and request.user == student and assgn.is_visible():
        params['student_view'] = True        
    else:
        return render(request, 'grader/access_denied.html', {'course': assgn.course})
        
    params['recent'] = subs[0]
    params['prev'] = subs[1:]
    params['status'] = Submission.STATUS_CHOICES[subs[0].status][1]
    
    if params.get('instructor_view') or params.get('ta_view'):
        
        #Get data from previous grading form
        if request.method == 'POST':
            form = GradeForm(subs[0], request.POST)
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
            form = GradeForm(subs[0])
        
        params['form'] = form
        
    return render(request, 'grader/submissions.html', params)
    
def submission_download(request, subid):
    """
    Returns a download response for the requested submission
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)
    
    #Get the submission
    sub = Submission.objects.filter(id=subid)[0]
    
    #Make sure user should be able to see this submission
    course = sub.assignment.course
    if not (sub.student == request.user or course.has_instructor(request.user) or course.has_ta(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})
    
    return get_download(os.path.join(sub.get_directory(), sub.get_filename()))
    
def course_file_download(request, courseid, filename):
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)
    
    #Get the course
    course = Course.objects.get(id=courseid)
    
    #Make sure user should be able to see this submission
    if not (course.has_user(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})
        
    return get_download(os.path.join(course.get_course_path(), filename))
    
def course_file_delete(request, courseid, filename):
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)
    
    #Get the course
    course = Course.objects.get(id=courseid)
    
    #Make sure user should be able to delete this file
    if not (course.has_instructor(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})
        
    os.remove(os.path.join(course.get_course_path(), filename))
        
    return HttpResponseRedirect(reverse('grader:course', args=(course.id,)))
    
def assgn_file_download(request, assgnid, filename):
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)
    
    #Get the course
    assgn = Assignment.objects.get(id=assgnid)
    
    #Make sure user should be able to see this submission
    if not (assgn.course.has_user(request.user)):
        return render(request, 'grader/access_denied.html', {'course': assgn.course})
        
    return get_download(os.path.join(assgn.get_assignment_path(), filename))
    
def assgn_file_delete(request, assgnid, filename):
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)
    
    #Get the course
    assgn = Assignment.objects.get(id=assgnid)
    
    #Make sure user should be able to delete this file
    if not (assgn.course.has_instructor(request.user)):
        return render(request, 'grader/access_denied.html', {'course': assgn.course})
        
    os.remove(os.path.join(assgn.get_assignment_path(), filename))
        
    return HttpResponseRedirect(reverse('grader:assignment', args=(assgn.id,)))
    
def get_download(filename):
    basename = os.path.basename(filename)
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(filename, 'rb'), chunk_size),
                           content_type=mimetypes.guess_type(filename)[0])
    response['Content-Length'] = os.path.getsize(filename)    
    response['Content-Disposition'] = "attachment; filename=%s" % basename
    return response


def edit_assgn(request, courseid, assgnid=None):
    """
    Renders a page for adding an assignment to a course

    In the future should only be visible to instructors
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)

    #Get the course to add the assignment to
    course = Course.objects.get(id=courseid)
    
    #Make sure user should be able to create assignments
    if not (course.has_instructor(request.user) or course.has_ta(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})
        
    #Get the assignment if provided
    if assgnid:
        assgn = Assignment.objects.get(id=assgnid)
    else:
        assgn = None
    

    #If the form is submitted, get the data
    if request.method == 'POST':
        form = AssgnForm(request.POST, instance=assgn)
        form.instance.course = course

        #Save the assignemnt
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('grader:assignment', args=(form.instance.id,)))

    #Create a new form and render the page
    else:
        form = AssgnForm(instance=assgn)
        
    return render(request, 'grader/edit_assgn.html', {'course': course, 'form': form})

DELIM_RE = re.compile(r", *|[\n\r]*")

def edit_course(request, courseid=None):
    """
    Renders a page for adding a course

    In the future should only be visible to instructors
    """
    
    #Make sure user is logged in
    if not load_user_groups(request.user):
        return login_redirect(request)
    
    #Load course data
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
    #Todo: only certain users should be able to create courses in the first place
    #if (not course and not request.user.is_faculty) or not (course and (course.has_instructor(request.user) or course.has_ta(request.user))):
    if not (request.user.is_superuser or (course and (course.has_instructor(request.user) or course.has_ta(request.user))) or (not course and request.user.is_faculty)):
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
            form.instance.instructors = instructors
            form.instance.students = students
            form.instance.tas = tas
            form.save()
            
            return HttpResponseRedirect(reverse('grader:course', args=(form.instance.id,)))
        
    #Create a new form and render the page
    else:
        form = CourseForm(instance=course, initial=form_data)
        
    return render(request, 'grader/edit_course.html', {'form': form})




