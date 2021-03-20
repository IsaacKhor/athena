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


def submission_download(request, subid, subdir=None, filename=None):
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
    
    if subdir and filename:
        
        for path, dirs, rfnames in os.walk(sub.get_directory(subdir=subdir)):
            if filename in rfnames:
                return get_download(os.path.join(path, filename))
    else:
        return get_download(os.path.join(sub.get_directory(), sub.get_filename()))

def submission_delete(request, subid, subdir, filename):
    
    #Make sure user is logged in
    if not request.user.is_authenticated():
        return login_redirect(request)
    
    #Get the course
    sub = Submission.objects.filter(id=subid)[0]
    
    #Make sure user should be able to delete this file
    course = sub.assignment.course
    if not (course.has_ta(request.user) or course.has_instructor(request.user) or course.has_student(request.user)):
        return render(request, 'grader/access_denied.html', {'course': course})
    
    for path, dirs, rfnames in os.walk(sub.get_directory(subdir=subdir)):
        if filename in rfnames:
            os.remove(os.path.join(path, filename))
        
    return HttpResponseRedirect(reverse('grader:submissions', args=(sub.assignment.id,sub.student.id,)))
    
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
