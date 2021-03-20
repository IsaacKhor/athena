from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from grader import views, file_access

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^course/(?P<courseid>[0-9]+)$', views.course, name='course'),
    url(r'^add_assgn/(?P<courseid>[0-9]+)$', views.edit_assgn, name='add_assgn'),
    url(r'^edit_assgn/(?P<courseid>[0-9]+)/(?P<assgnid>[0-9]+)$', views.edit_assgn, name='edit_assgn'),
    url(r'^add_course/$', views.edit_course, name='add_course'),
    url(r'^edit_course/(?P<courseid>[0-9]+)$', views.edit_course, name='edit_course'),
    url(r'^assignment/(?P<assgnid>[0-9]+)$', views.assignment, name='assignment'),
    url(r'^submissions/(?P<assgnid>[0-9]+)/(?P<userid>[0-9]+)$', views.submissions, name='submissions'),
    
    url(r'^course/(?P<courseid>[0-9]+)/(?P<filename>[^/]+)$', file_access.course_file_download, name='course_file_download'),
    url(r'^course/(?P<courseid>[0-9]+)/delete_file/(?P<filename>[^/]+)$', file_access.course_file_delete, name='course_file_delete'),
    
    url(r'^assignment/(?P<assgnid>[0-9]+)/(?P<filename>[^/]+)$', file_access.assgn_file_download, name='assgn_file_download'),
    url(r'^assignment/(?P<assgnid>[0-9]+)/delete_file/(?P<filename>[^/]+)$', file_access.assgn_file_delete, name='assgn_file_delete'),
    
    url(r'^download_subfile/(?P<subid>[0-9]+)$', file_access.submission_download, name='submission_download'),
    url(r'^download_subfile/(?P<subid>[0-9]+)/(?P<subdir>[^/]+)/(?P<filename>[^/]+)$', file_access.submission_download, name='submission_download_subdir'),
    url(r'^delete_subfile/(?P<subid>[0-9]+)/(?P<subdir>[^/]+)/(?P<filename>[^/]+)$', file_access.submission_delete, name='submission_delete_subdir'),
    
    
    url(r'^remove_grade/(?P<gradeid>[0-9]+)', views.remove_grade, name='remove_grade'),
    url(r'^reset_autograde/(?P<gradeid>[0-9]+)', views.reset_autograde, name='reset_autograde'),
    
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    
)
