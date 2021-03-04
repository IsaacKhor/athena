from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.models import User, Group
import django.contrib.auth as auth
from grader.models import *
from grader.forms import *

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
    course = Course.objects.filter(id=courseid)[0]
    
    #Make sure user should be able to see this course
    if not course.has_user(request.user):
        return render(request, 'grader/access_denied.html', {'course': course})
    
    return render(request, 'grader/course.html', {'course': course})


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
    assgn = Assignment.objects.filter(id=assgnid)[0]
    
    #Make sure user should be able to see this assignment
    if not assgn.course.has_user(request.user):
        return render(request, 'grader/access_denied.html', {'course': assgn.course})

    #If the form has been submitted, get the data
    if request.method == 'POST':
        form = SubmitForm(assgn, request.POST, request.FILES)

        if form.is_valid():

            #Create a new submission from the form data
            student = User.objects.filter(id=form.cleaned_data['student'])[0]
            new_sub = Submission(assignment=assgn, student=student)
            new_sub.save()
            
            #Make submission directory
            if not os.path.exists(new_sub.get_directory()):
                os.makedirs(new_sub.get_directory())
            
            #Save submission
            filename = os.path.join(new_sub.get_directory(), form.cleaned_data['sub_file'].name)
            with open(filename, 'wb+') as f:
                for chunk in form.cleaned_data['sub_file'].chunks():
                    f.write(chunk)
            
            #Redirect back to the assignment page
            return HttpResponseRedirect(reverse('grader:assignment', args=(assgnid,)))

    #Create a new form
    else:
        form = SubmitForm(assgn)

    #Get list of submissions
    submissions = assgn.submission_set.all()

    #Render the page
    return render(request, 'grader/assignment.html', {'assgn': assgn, 'form': form, 'subs': submissions})


def grade(request, subid):
    """
    Renders a page for the instructor to grade a submission

    In the future should only be visible to instructors, not only for un-graded assignments
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)

    #Get the submission
    sub = Submission.objects.filter(id=subid)[0]
    
    #Make sure user should be able to see this submission
    course = sub.assignment.course
    if not (course.has_instructor(request.user) or course.has_ta(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})

    #If the form is submitted, get the data
    if request.method == 'POST':
        form = GradeForm(sub, request.POST)
        form.instance.submission = sub

        #Save the grade
        if form.is_valid():
            form.save()
            sub.status = Submission.CH_GRADED
            sub.save()

            #Redirect back to the assignment page
            return HttpResponseRedirect(reverse('grader:assignment', args=(sub.assignment.id,)))

    #Get the form and render the page
    else:
        form = GradeForm(sub)
    return render(request, 'grader/grade.html', {'sub': sub, 'form': form})


def submission(request, subid):
    """
    Renders a page for a student to view their submission

    In the future should only be visible to the student who submitted it
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
        
    return render(request, 'grader/submission.html', {'sub': sub})
    
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
    
    #Get the path to save the file
    path = sub.get_directory()
    filename = sub.get_filename()
    full_file = os.path.join(path, filename)
    
    #Return a streaming response
    chunk_size = 8192
    response = StreamingHttpResponse(FileWrapper(open(full_file, 'rb'), chunk_size),
                           content_type=mimetypes.guess_type(full_file)[0])
    response['Content-Length'] = os.path.getsize(full_file)    
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


def add_assgn(request, courseid):
    """
    Renders a page for adding an assignment to a course

    In the future should only be visible to instructors
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)

    #Get the course to add the assignment to
    course = Course.objects.filter(id=courseid)[0]
    
    #Make sure user should be able to create assignments
    if not (course.has_instructor(request.user) or course.has_ta(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})

    #If the form is submitted, get the data
    if request.method == 'POST':
        form = AssgnForm(request.POST)
        form.instance.course = course

        #Save the assignemnt
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('grader:course', args=(courseid,)))

    #Create a new form and render the page
    else:
        form = AssgnForm()
    return render(request, 'grader/add_assgn.html', {'course': course, 'form': form})

DELIM_RE = re.compile(r", *|[\n\r]*")

def edit_course(request, courseid=None):
    """
    Renders a page for adding a course

    In the future should only be visible to instructors
    """
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
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
    if not course or not (course.has_instructor(request.user) or course.has_ta(request.user)):
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




