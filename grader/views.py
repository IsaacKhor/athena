from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from grader.models import *
from grader.forms import *
from django.core.urlresolvers import reverse

def home(request):
    """
    Renders home page
    For now simply shows all courses

    In the future it should show user's enrolled courses or courses they teach, depending on roll
    """

    #Get all the courses and render the template
    courses = Course.objects.all()
    return render(request, 'grader/home.html', {'course_list': courses})


def course(request, courseid):
    """
    Renders course page
    Shows course description, assignments, students, instructors, and TA
    """

    #Get the course and render the template
    course = Course.objects.filter(id=courseid)[0]
    return render(request, 'grader/course.html', {'course': course})


def assignment(request, assgnid):
    """
    Renders assignment page
    Shows what course it's part of, descriptions, submission for, and submissions so far

    In the future it should only show submit form for students,
    only show submissions so far for instructors/TAs.
    """

    #Get the assigment
    assgn = Assignment.objects.filter(id=assgnid)[0]

    #If the form has been submitted, get the data
    if request.method == 'POST':
        form = SubmitForm(assgn, request.POST, request.FILES)

        if form.is_valid():

            #For now just print the contents of the file
            #it should really save the file on the disk!
            print (form.cleaned_data['sub_file'].read())

            #Create a new submission from the form data
            student = User.objects.filter(id=form.cleaned_data['student'])[0]
            new_sub = Submission(assignment=assgn, student=student)
            new_sub.save()

            #Redirect back to the assignment page
            return HttpResponseRedirect(reverse('assignment', args=(assgnid,)))

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

    #Get the submission
    sub = Submission.objects.filter(id=subid)[0]

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
            return HttpResponseRedirect(reverse('assignment', args=(sub.assignment.id,)))

    #Get the form and render the page
    else:
        form = GradeForm(sub)
    return render(request, 'grader/grade.html', {'sub': sub, 'form': form})


def submission(request, subid):
    """
    Renders a page for a student to view their submission

    In the future should only be visible to the student who submitted it
    """

    #Get the submission and render the page
    sub = Submission.objects.filter(id=subid)[0]
    return render(request, 'grader/submission.html', {'sub': sub})


def add_assgn(request, courseid):
    """
    Renders a page for adding an assignment to a course

    In the future should only be visible to instructors
    """

    #Get the course to add the assignment to
    course = Course.objects.filter(id=courseid)[0]

    #If the form is submitted, get the data
    if request.method == 'POST':
        form = AssgnForm(request.POST)
        form.instance.course = course

        #Save the assignemnt
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('course', args=(courseid,)))

    #Create a new form and render the page
    else:
        form = AssgnForm()
    return render(request, 'grader/add_assgn.html', {'course': course, 'form': form})
