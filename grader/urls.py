from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from grader import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^course/(?P<courseid>[0-9]+)$', views.course, name='course'),
    url(r'^add_assgn/(?P<courseid>[0-9]+)$', views.add_assgn, name='add_assgn'),
    url(r'^add_course/$', views.edit_course, name='add_course'),
    url(r'^edit_course/(?P<courseid>[0-9]+)$', views.edit_course, name='edit_course'),
    url(r'^assignment/(?P<assgnid>[0-9]+)$', views.assignment, name='assignment'),
    url(r'^grade/(?P<subid>[0-9]+)$', views.grade, name='grade'),
    url(r'^submission/(?P<subid>[0-9]+)$', views.submission, name='submission'),
    url(r'^submission/(?P<subid>[0-9]+)/download$', views.submission_download, name='submission_download'),
    
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    
)
