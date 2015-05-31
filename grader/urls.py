from django.conf.urls import patterns, include, url

from grader import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^course/(?P<courseid>[0-9]+)$', views.course, name='course'),
    url(r'^add_assgn/(?P<courseid>[0-9]+)$', views.add_assgn, name='add_assgn'),
    url(r'^assignment/(?P<assgnid>[0-9]+)$', views.assignment, name='assignment'),
    url(r'^grade/(?P<subid>[0-9]+)$', views.grade, name='grade'),
    url(r'^submission/(?P<subid>[0-9]+)$', views.submission, name='submission'),
)
